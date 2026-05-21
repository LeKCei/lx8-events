import Foundation
import Vision
import AppKit

let imagePath = "/Users/alexei.ferreira/.gemini/antigravity/brain/3251c28c-63f6-4664-adc4-19c8957f68de/test_frame_5s.jpg"
guard let image = NSImage(contentsOfFile: imagePath) else {
    print("Failed to load image at \(imagePath)")
    exit(1)
}

guard let tiffData = image.tiffRepresentation,
      let bitmap = NSBitmapImageRep(data: tiffData),
      let cgImage = bitmap.cgImage else {
    print("Failed to get CGImage")
    exit(1)
}

let requestHandler = VNImageRequestHandler(cgImage: cgImage, options: [:])
let request = VNRecognizeTextRequest { request, error in
    if let error = error {
        print("Error: \(error)")
        return
    }
    guard let observations = request.results as? [VNRecognizedTextObservation] else { return }
    print("Found \(observations.count) text segments:")
    for (index, observation) in observations.enumerated() {
        if let candidate = observation.topCandidates(1).first {
            let box = observation.boundingBox
            print(String(format: "[%02d] (x: %.3f, y: %.3f, w: %.3f, h: %.3f) Conf: %.2f -> %@", 
                         index, box.origin.x, box.origin.y, box.size.width, box.size.height, candidate.confidence, candidate.string))
        }
    }
}
request.recognitionLevel = .accurate

do {
    try requestHandler.perform([request])
} catch {
    print("Error performing request: \(error)")
}
