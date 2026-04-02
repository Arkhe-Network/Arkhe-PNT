import Foundation

public class OrbVM {
    private var coherence: Double = 1.6180339887
    private var state: UInt64 = 0

    public init() {}

    public func executeCycle() {
        self.state += 1
        self.coherence *= 1.0001
    }

    public func getCoherence() -> Double {
        return self.coherence
    }
}
