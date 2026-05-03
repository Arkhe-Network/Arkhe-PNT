// sophon_v2_hexagon.wgsl — Corrected & Enhanced Version
// Fixes: array initialization, derivative accuracy, mode switching logic

struct Uniforms {
    time: f32,
    resolution: vec2<f32>,
    speed: f32,

    // Cavity geometry
    hex_radius: f32,
    parabolic_depth: f32,

    // Six coherent waves (arrays must be initialized in Python)
    wave_amplitude: array<f32, 6>,
    wave_frequency: array<f32, 6>,
    wave_phase: array<f32, 6>,
    wave_direction: array<vec2<f32>, 6>,

    // Coupling & visualization
    coupling_strength: f32,
    coherence_threshold: f32,
    mode: f32,  // 0=intensity, 1=isosurface, 2=topology
    color1: vec3<f32>,
    color2: vec3<f32>,
    color3: vec3<f32>,
};

@group(0) @binding(0) var<uniform> u: Uniforms;

// ============================================================
// 1. HEXAGONAL CAVITY GEOMETRY (Corrected)
// ============================================================

fn hex_distance(p: vec2<f32>, radius: f32) -> f32 {
    // Signed distance to regular hexagon (positive = outside)
    let angle = atan2(p.y, p.x);
    // 6 sectors of 60° = π/3 ≈ 1.0472 rad
    let sector_angle = 1.0471975512;
    let half_sector = sector_angle * 0.5;  // π/6 ≈ 0.5236

    // Find nearest sector normal
    let sector = floor((angle + half_sector) / sector_angle);
    let normal_angle = sector * sector_angle;
    let normal = vec2<f32>(cos(normal_angle), sin(normal_angle));

    // Distance to hexagon edge
    let d = dot(p, normal) - radius * cos(half_sector);
    return d;
}

fn parabolic_z(xy: vec2<f32>, radius: f32, depth: f32) -> f32 {
    // Parabolic profile: z = depth · (r/radius)², clamped to [0, depth]
    let r = length(xy);
    let r_norm = clamp(r / radius, 0.0, 1.0);
    return depth * r_norm * r_norm;
}

fn cavity_sdf(p: vec3<f32>) -> f32 {
    // Signed distance function for hexagonal parabolic cavity
    let hex_d = hex_distance(p.xy, u.hex_radius);
    let z_max = parabolic_z(p.xy, u.hex_radius, u.parabolic_depth);
    let z_d = max(p.z - z_max, -p.z);  // Distance to z-bounds [0, z_max]
    return max(hex_d, z_d);
}

// ============================================================
// 2. SIX-WAVE COHERENT SUPERPOSITION (Enhanced)
// ============================================================

fn wave_field(p: vec3<f32>, t: f32) -> f32 {
    var field: f32 = 0.0;

    for (var i: i32 = 0; i < 6; i++) {
        // Plane wave: A·cos(k·r - ωt + φ)
        let k = u.wave_direction[i] * u.wave_frequency[i];
        let phase = dot(k, p.xy) - u.speed * u.wave_frequency[i] * t + u.wave_phase[i];

        // Spatial envelope: hexagonal aperture + parabolic vertical profile
        let hex_env = smoothstep(0.02, 0.0, hex_distance(p.xy, u.hex_radius));
        let z_max = parabolic_z(p.xy, u.hex_radius, u.parabolic_depth);
        let z_env = smoothstep(1.0, 0.98, p.z / max(z_max, 0.001));

        field += u.wave_amplitude[i] * cos(phase) * hex_env * z_env;
    }

    // Nonlinear mode coupling (adjacent waves only)
    if (u.coupling_strength > 0.0) {
        var coupling: f32 = 0.0;
        for (var i: i32 = 0; i < 6; i++) {
            let j = (i + 1) % 6;
            let k_i = u.wave_direction[i] * u.wave_frequency[i];
            let k_j = u.wave_direction[j] * u.wave_frequency[j];
            let phase_i = dot(k_i, p.xy) - u.speed * u.wave_frequency[i] * t + u.wave_phase[i];
            let phase_j = dot(k_j, p.xy) - u.speed * u.wave_frequency[j] * t + u.wave_phase[j];
            // Product of adjacent modes → sum/difference frequencies
            coupling += sin(phase_i) * sin(phase_j);
        }
        field += coupling * u.coupling_strength * 0.5;
    }

    return field;
}

fn field_gradient(p: vec3<f32>, t: f32) -> vec3<f32> {
    // Central difference gradient with adaptive step
    let base_step = 0.001;
    let eps = base_step * (1.0 + 0.1 * abs(wave_field(p, t)));  // Adaptive

    return vec3<f32>(
        wave_field(p + vec3<f32>(eps, 0.0, 0.0), t) - wave_field(p - vec3<f32>(eps, 0.0, 0.0), t),
        wave_field(p + vec3<f32>(0.0, eps, 0.0), t) - wave_field(p - vec3<f32>(0.0, eps, 0.0), t),
        wave_field(p + vec3<f32>(0.0, 0.0, eps), t) - wave_field(p - vec3<f32>(0.0, 0.0, eps), t)
    ) / (2.0 * eps);
}

// ============================================================
// 3. ADAPTIVE RAY MARCHING (Optimized)
// ============================================================

fn ray_march(ro: vec3<f32>, rd: vec3<f32>) -> vec4<f32> {
    var t_dist: f32 = 0.0;
    var pos: vec3<f32>;
    var accumulated_intensity: f32 = 0.0;

    // Early exit: ray misses cavity bounding sphere
    let bounding_r = u.hex_radius * 1.3;
    let to_center = -ro;
    let closest = dot(to_center, rd);
    if (closest < 0.0 && length(to_center) > bounding_r) { discard; }

    for (var i: i32 = 0; i < 150; i++) {
        pos = ro + rd * t_dist;

        // Outside cavity: fast march
        if (cavity_sdf(pos) > 0.01) {
            t_dist += 0.15;
            if (t_dist > 25.0) { break; }
            continue;
        }

        let field = wave_field(pos, u.time * u.speed);

        if (u.mode == 0.0) {
            // Mode 0: Volume rendering with absorption
            let density = abs(field) * 0.08;
            accumulated_intensity += density * exp(-accumulated_intensity * 2.0);
            t_dist += max(0.02, 0.1 - density);
        }
        else if (u.mode == 1.0) {
            // Mode 1: Coherence isosurface
            let d = abs(abs(field) - u.coherence_threshold);
            if (d < 0.003) {
                // Surface hit: compute lighting
                let n = normalize(field_gradient(pos, u.time * u.speed));
                let light = normalize(vec3<f32>(0.8, 1.2, 0.6));
                let diff = max(dot(n, light), 0.15);
                let view = normalize(ro - pos);
                let fres = pow(1.0 - max(dot(n, view), 0.0), 4.0);

                // Color based on position and field sign
                let hue = atan2(pos.y, pos.x) * 0.159 + 0.5;  // [0,1]
                let base_col = mix(u.color1, u.color2, hue);
                let col = mix(base_col, u.color3, fres * 0.5) * diff;

                return vec4<f32>(col, 1.0);
            }
            t_dist += d * 0.4;
        }
        else {
            // Mode 2: Topological gradient visualization
            let grad = length(field_gradient(pos, u.time * u.speed));
            let d = 0.015 / (grad + 0.002);
            t_dist += d;
        }

        if (t_dist > 25.0) { break; }
    }

    // Volume rendering final composition
    if (u.mode == 0.0 && accumulated_intensity > 0.01) {
        let intensity = min(accumulated_intensity * 1.5, 1.0);
        let hue = fract(accumulated_intensity * 0.2 + u.time * 0.05);
        let col = mix(u.color1, u.color2, hue);
        return vec4<f32>(mix(col, u.color3, intensity) * intensity, 1.0);
    }

    discard;
    return vec4<f32>(0.0);
}

@fragment
fn fs_main(@builtin(position) coord: vec4<f32>) -> @location(0) vec4<f32> {
    // Normalized device coordinates
    let uv = (coord.xy / u.resolution) * 2.0 - 1.0;
    let aspect = u.resolution.x / u.resolution.y;

    // Orbiting camera with hexagonal symmetry
    let cam_angle = u.time * 0.12;  // Slow orbit
    let cam_radius = u.hex_radius * 3.0;
    let cam_height = u.parabolic_depth * 1.8;

    let ro = vec3<f32>(
        cos(cam_angle) * cam_radius,
        sin(cam_angle) * cam_radius,
        cam_height
    );
    let look_at = vec3<f32>(0.0, 0.0, u.parabolic_depth * 0.4);

    // Camera basis
    let forward = normalize(look_at - ro);
    let world_up = vec3<f32>(0.0, 0.0, 1.0);
    let right = normalize(cross(forward, world_up));
    let up = cross(right, forward);

    // Ray direction through pixel
    let rd = normalize(forward + right * uv.x * aspect + up * uv.y);

    return ray_march(ro, rd);
}
