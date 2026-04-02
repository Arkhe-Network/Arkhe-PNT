pub mod arkhe {
    pub mod teknet {
        pub mod v1 {
            tonic::include_proto!("arkhe.teknet.v1");
        }
    }
}

pub use arkhe::teknet::v1::*;
