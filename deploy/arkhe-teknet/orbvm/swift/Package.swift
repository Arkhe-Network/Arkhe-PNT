// swift-tools-version: 5.7
import PackageDescription

let package = Package(
    name: "OrbVM",
    products: [
        .library(name: "OrbVM", targets: ["OrbVM"]),
    ],
    targets: [
        .target(name: "OrbVM", dependencies: []),
    ]
)
