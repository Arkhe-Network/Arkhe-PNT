use clap::Parser;
use tokio;

mod commands;

use commands::shard::{ShardArgs, handle_shard_create};
use commands::self_complete::{SelfCompleteArgs, handle_self_complete};

#[derive(Parser)]
enum Commands {
    Shard(ShardArgs),
    /// Fecha o ciclo: analisa, gera, prova e implanta novos módulos
    SelfComplete(SelfCompleteArgs),
}

#[derive(Parser)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    match cli.command {
        Commands::Shard(args) => handle_shard_create(args).await,
        Commands::SelfComplete(args) => handle_self_complete(args).await,
    }
}
