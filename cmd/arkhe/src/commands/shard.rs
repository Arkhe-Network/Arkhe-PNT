use clap::Parser;

#[derive(Parser)]
pub struct ShardArgs {
    #[arg(long, default_value = "6064")]
    pub substrate: String,
    #[arg(long)]
    pub motor: String,
    #[arg(long)]
    pub gpu: bool,
}

pub async fn handle_shard_create(args: ShardArgs) -> Result<(), Box<dyn std::error::Error>> {
    println!("Shard criado (mock): substrate={}, motor={}, gpu={}", args.substrate, args.motor, args.gpu);
    Ok(())
}
