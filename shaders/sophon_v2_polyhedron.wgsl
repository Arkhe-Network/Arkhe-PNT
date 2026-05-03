// sophon_v2_polyhedron.wgsl — Generalized Polyhedral Interference with 3D Raymarching
struct Uniforms {
    time: f32,
    pad0: f32, // Padding to align vec2<f32> resolution
    resolution: vec2<f32>,
    speed: f32,

    // Geometry
    radius: f32,
    parabolic_depth: f32,
    pad1: f32, // Pad to reach 32 byte boundary before array

    // Wave parameters
    // Arrays inside uniforms have a 16-byte stride per element.
    // We use vec4<f32> where the first element is the value to respect memory layout naturally.
    wave_amplitude: array<vec4<f32>, 20>,
    wave_frequency: array<vec4<f32>, 20>,
    wave_phase: array<vec4<f32>, 20>,
    wave_direction: array<vec4<f32>, 20>, // xy contains direction

    num_waves: f32, // Passed as float to avoid bitwise reinterpretation from Python float32 buffer
    coupling_strength: f32,
    coherence_threshold: f32,
    mode: f32,

    color1: vec4<f32>, // vec4 for alignment
    color2: vec4<f32>,
    color3: vec4<f32>,
};

@group(0) @binding(0) var<uniform> u: Uniforms;

fn poly_distance(p: vec2<f32>, radius: f32) -> f32 {
    return length(p) - radius; // Approximate bounding cylinder
}

fn parabolic_z(xy: vec2<f32>, radius: f32, depth: f32) -> f32 {
    let r = length(xy);
    let r_norm = clamp(r / radius, 0.0, 1.0);
    return depth * r_norm * r_norm;
}

fn cavity_sdf(p: vec3<f32>) -> f32 {
    let poly_d = poly_distance(p.xy, u.radius);
    let z_max = parabolic_z(p.xy, u.radius, u.parabolic_depth);
    let z_d = max(p.z - z_max, -p.z);
    return max(poly_d, z_d);
}

fn wave_field(p: vec3<f32>, t: f32) -> f32 {
    var field: f32 = 0.0;
    let n_waves = i32(u.num_waves);

    for (var i: i32 = 0; i < 20; i++) {
        if (i >= n_waves) { break; }

        let k = u.wave_direction[i].xy * u.wave_frequency[i].x;
        let phase = dot(k, p.xy) - u.speed * u.wave_frequency[i].x * t + u.wave_phase[i].x;

        let poly_env = smoothstep(0.02, 0.0, poly_distance(p.xy, u.radius));
        let z_max = parabolic_z(p.xy, u.radius, u.parabolic_depth);
        let z_env = smoothstep(1.0, 0.98, p.z / max(z_max, 0.001));

        field += u.wave_amplitude[i].x * cos(phase) * poly_env * z_env;
    }

    if (u.coupling_strength > 0.0) {
        var coupling: f32 = 0.0;
        for (var i: i32 = 0; i < 20; i++) {
            if (i >= n_waves) { break; }
            let j = (i + 1) % n_waves;
            let k_i = u.wave_direction[i].xy * u.wave_frequency[i].x;
            let k_j = u.wave_direction[j].xy * u.wave_frequency[j].x;
            let phase_i = dot(k_i, p.xy) - u.speed * u.wave_frequency[i].x * t + u.wave_phase[i].x;
            let phase_j = dot(k_j, p.xy) - u.speed * u.wave_frequency[j].x * t + u.wave_phase[j].x;
            coupling += sin(phase_i) * sin(phase_j);
        }
        field += coupling * u.coupling_strength * 0.5;
    }

    return field;
}

fn field_gradient(p: vec3<f32>, t: f32) -> vec3<f32> {
    let base_step = 0.001;
    let eps = base_step * (1.0 + 0.1 * abs(wave_field(p, t)));

    return vec3<f32>(
        wave_field(p + vec3<f32>(eps, 0.0, 0.0), t) - wave_field(p - vec3<f32>(eps, 0.0, 0.0), t),
        wave_field(p + vec3<f32>(0.0, eps, 0.0), t) - wave_field(p - vec3<f32>(0.0, eps, 0.0), t),
        wave_field(p + vec3<f32>(0.0, 0.0, eps), t) - wave_field(p - vec3<f32>(0.0, 0.0, eps), t)
    ) / (2.0 * eps);
}

fn ray_march(ro: vec3<f32>, rd: vec3<f32>) -> vec4<f32> {
    var t_dist: f32 = 0.0;
    var pos: vec3<f32>;
    var accumulated_intensity: f32 = 0.0;

    let bounding_r = u.radius * 1.3;
    let to_center = -ro;
    let closest = dot(to_center, rd);
    if (closest < 0.0 && length(to_center) > bounding_r) { discard; }

    for (var i: i32 = 0; i < 150; i++) {
        pos = ro + rd * t_dist;

        if (cavity_sdf(pos) > 0.01) {
            t_dist += 0.15;
            if (t_dist > 25.0) { break; }
            continue;
        }

        let field = wave_field(pos, u.time * u.speed);

        if (u.mode == 0.0) {
            let density = abs(field) * 0.08;
            accumulated_intensity += density * exp(-accumulated_intensity * 2.0);
            t_dist += max(0.02, 0.1 - density);
        }
        else if (u.mode == 1.0) {
            let d = abs(abs(field) - u.coherence_threshold);
            if (d < 0.003) {
                let n = normalize(field_gradient(pos, u.time * u.speed));
                let light = normalize(vec3<f32>(0.8, 1.2, 0.6));
                let diff = max(dot(n, light), 0.15);
                let view = normalize(ro - pos);
                let fres = pow(1.0 - max(dot(n, view), 0.0), 4.0);

                let hue = atan2(pos.y, pos.x) * 0.159 + 0.5;
                let base_col = mix(u.color1.rgb, u.color2.rgb, hue);
                let col = mix(base_col, u.color3.rgb, fres * 0.5) * diff;

                return vec4<f32>(col, 1.0);
            }
            t_dist += d * 0.4;
        }
        else {
            let grad = length(field_gradient(pos, u.time * u.speed));
            let d = 0.015 / (grad + 0.002);
            t_dist += d;
        }

        if (t_dist > 25.0) { break; }
    }

    if (u.mode == 0.0 && accumulated_intensity > 0.01) {
        let intensity = min(accumulated_intensity * 1.5, 1.0);
        let hue = fract(accumulated_intensity * 0.2 + u.time * 0.05);
        let col = mix(u.color1.rgb, u.color2.rgb, hue);
        return vec4<f32>(mix(col, u.color3.rgb, intensity) * intensity, 1.0);
    }

    discard;
    return vec4<f32>(0.0);
}

@fragment
fn fs_main(@builtin(position) coord: vec4<f32>) -> @location(0) vec4<f32> {
    let uv = (coord.xy / u.resolution) * 2.0 - 1.0;
    let aspect = u.resolution.x / u.resolution.y;

    let cam_angle = u.time * 0.12;
    let cam_radius = u.radius * 3.0;
    let cam_height = u.parabolic_depth * 1.8;

    let ro = vec3<f32>(
        cos(cam_angle) * cam_radius,
        sin(cam_angle) * cam_radius,
        cam_height
    );
    let look_at = vec3<f32>(0.0, 0.0, u.parabolic_depth * 0.4);

    let forward = normalize(look_at - ro);
    let world_up = vec3<f32>(0.0, 0.0, 1.0);
    let right = normalize(cross(forward, world_up));
    let up = cross(right, forward);

    let rd = normalize(forward + right * uv.x * aspect + up * uv.y);

    return ray_march(ro, rd);
}
