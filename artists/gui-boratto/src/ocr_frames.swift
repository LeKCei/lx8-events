import Foundation
import Vision
import AppKit

let frames = [0, 3, 6, 9, 12, 15]

for frame in frames {
    let imagePath = "/Users/alexei.ferreira/Events/guiboratto_post/frame_\(frame).jpg"
    print("\n--- OCR Results for Frame at \(frame)s (\(imagePath)) ---")
    
    guard let image = NSImage(contentsOfFile: imagePath) else {
        print("Failed to load image at \(imagePath)")
        continue
    }
    
    guard let tiffData = image.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: tiffData),
          let cgImage = bitmap.cgImage else {
        print("Failed to get CGImage from \(imagePath)")
        continue
    }
    
    let requestHandler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    let request = VNRecognizeTextRequest { request, error in
        if let error = error {
            print("Error: \(error)")
            return
        }
        guard let observations = request.results as? [VNRecognizedTextObservation] else { return }
        for observation in observations {
            if let candidate = observation.topCandidates(1).first {
                print(candidate.string)
            }
        }
    }
    request.recognitionLevel = .accurate
    
    do {
        try requestHandler.perform([request])
    } catch {
        print("Unable to perform request: \(error)")
    }
}
