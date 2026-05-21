import AVFoundation
import Foundation
import CoreGraphics
import ImageIO

func extractFrames(videoPath: String, outputPrefix: String, times: [Double]) {
    let videoURL = URL(fileURLWithPath: videoPath)
    let asset = AVAsset(url: videoURL)
    let generator = AVAssetImageGenerator(asset: asset)
    generator.appliesPreferredTrackTransform = true
    generator.requestedTimeToleranceBefore = .zero
    generator.requestedTimeToleranceAfter = .zero
    
    for time in times {
        let cmTime = CMTime(seconds: time, preferredTimescale: 600)
        do {
            let cgImage = try generator.copyCGImage(at: cmTime, actualTime: nil)
            let outPath = "/Users/alexei.ferreira/Events/guiboratto_post/\(outputPrefix)_frame_\(Int(time)).jpg"
            let fileURL = URL(fileURLWithPath: outPath)
            
            guard let destination = CGImageDestinationCreateWithURL(fileURL as CFURL, kUTTypeJPEG, 1, nil) else {
                print("Failed to create image destination for \(outPath)")
                continue
            }
            
            let properties = [kCGImageDestinationLossyCompressionQuality: 0.85] as CFDictionary
            CGImageDestinationAddImage(destination, cgImage, properties)
            if CGImageDestinationFinalize(destination) {
                print("Extracted: \(outPath)")
            } else {
                print("Failed to finalize: \(outPath)")
            }
        } catch {
            print("Failed to extract frame at \(time)s from \(videoPath): \(error)")
        }
    }
}

let tourPath = "/Users/alexei.ferreira/Events/guiboratto_post/gui_boratto_tour_promo.mp4"
let eventPath = "/Users/alexei.ferreira/Events/guiboratto_post/gui_boratto_barcelona_promo.mp4"

print("Extracting frames from Tour Promo video...")
extractFrames(videoPath: tourPath, outputPrefix: "tour_promo", times: [3.0, 12.0])

print("\nExtracting frames from Barcelona Event Promo video...")
extractFrames(videoPath: eventPath, outputPrefix: "barcelona_promo", times: [3.0, 12.0])
