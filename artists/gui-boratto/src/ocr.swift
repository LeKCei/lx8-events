import Foundation
import Vision
import AppKit

let imagePath = "/Users/alexei.ferreira/Events/guiboratto_post/reference.JPG"
guard let image = NSImage(contentsOfFile: imagePath) else {
    print("Failed to load image at \(imagePath)")
    exit(1)
}

guard let tiffData = image.tiffRepresentation,
      let bitmap = NSBitmapImageRep(data: tiffData),
      let cgImage = bitmap.cgImage else {
    print("Failed to get CGImage from \(imagePath)")
    exit(1)
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
request.recognitionLevel = VNRequestTextRecognitionLevel.accurate

do {
    try requestHandler.perform([request])
} catch {
    print("Unable to perform request: \(error)")
}
