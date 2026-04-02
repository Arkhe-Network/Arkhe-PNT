// archimedes-processor.js
// AudioWorkletProcessor for VLF (Very Low Frequency) FSK Modulation

class ArchimedesProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.phase = 0;
    this.sampleRate = 192000; // High-res for SDR
    
    // FSK Frequencies (VLF band transposed for audio processing)
    // In a real SDR setup, this would be upconverted.
    // Here we use audio frequencies for demonstration.
    this.markFreq = 1200;  // Logic 1
    this.spaceFreq = 2200; // Logic 0
    
    this.baudRate = 300;
    this.samplesPerSymbol = this.sampleRate / this.baudRate;
    this.currentSample = 0;
    
    this.dataBuffer = [];
    this.currentBitIndex = 0;
    this.currentByte = 0;
    this.isTransmitting = false;

    this.port.onmessage = (event) => {
      if (event.data.type === 'DATA_STREAM') {
        // Convert payload to binary array
        const payload = event.data.payload;
        for (let i = 0; i < payload.length; i++) {
          this.dataBuffer.push(payload.charCodeAt(i));
        }
        if (!this.isTransmitting && this.dataBuffer.length > 0) {
          this.startNextByte();
        }
      }
    };
  }

  startNextByte() {
    if (this.dataBuffer.length > 0) {
      this.currentByte = this.dataBuffer.shift();
      this.currentBitIndex = 0;
      this.currentSample = 0;
      this.isTransmitting = true;
    } else {
      this.isTransmitting = false;
    }
  }

  process(inputs, outputs, parameters) {
    const output = outputs[0];
    const channel = output[0];

    for (let i = 0; i < channel.length; i++) {
      if (this.isTransmitting) {
        // Extract current bit (LSB first)
        const bit = (this.currentByte >> this.currentBitIndex) & 1;
        
        // Select frequency based on bit
        const freq = bit === 1 ? this.markFreq : this.spaceFreq;
        
        // Generate sine wave (I/Q modulation base)
        const phaseIncrement = (2 * Math.PI * freq) / this.sampleRate;
        this.phase += phaseIncrement;
        if (this.phase >= 2 * Math.PI) {
          this.phase -= 2 * Math.PI;
        }
        
        channel[i] = Math.sin(this.phase);

        this.currentSample++;
        
        // Move to next bit after samplesPerSymbol
        if (this.currentSample >= this.samplesPerSymbol) {
          this.currentSample = 0;
          this.currentBitIndex++;
          
          // Move to next byte after 8 bits
          if (this.currentBitIndex >= 8) {
            this.startNextByte();
          }
        }
      } else {
        // Idle state (transmit mark frequency or silence)
        channel[i] = 0; 
      }
    }

    return true; // Keep processor alive
  }
}

registerProcessor('archimedes-processor', ArchimedesProcessor);
