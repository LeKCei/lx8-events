import AVFoundation
import Foundation
import CoreGraphics
import ImageIO

let videoURL = URL(fileURLWithPath: "/Users/alexei.ferreira/Events/guiboratto_post/VIDEO-2025-05-08-17-54-08.mp4")
let asset = AVAsset(url: videoURL)
let generator = AVAssetImageGenerator(asset: asset)
generator.appliesPreferredTrackTransform = true

// Request exact times
generator.requestedTimeToleranceBefore = .zero
generator.requestedTimeToleranceAfter = .zero

let times: [Double] = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]

for time in times {
    let cmTime = CMTime(seconds: time, preferredTimescale: 600)
    do {
        let cgImage = try generator.copyCGImage(at: cmTime, actualTime: nil)
        let fileURL = URL(fileURLWithPath: "/Users/alexei.ferreira/Events/guiboratto_post/frame_\(Int(time)).jpg")
        
        guard let destination = CGImageDestinationCreateWithURL(fileURL as CFURL, kUTTypeJPEG, 1, nil) else {
            print("Failed to create image destination for frame at \(time)s")
            continue
        }
        
        let properties = [kCGImageDestinationLossyCompressionQuality: 0.8] as CFDictionary
        CGImageDestinationAddImage(destination, cgImage, properties)
        if CGImageDestinationFinalize(destination) {
            print("Extracted frame at \(time)s -> \(fileURL.lastPathComponent)")
        } else {
            print("Failed to write frame at \(time)s")
        }
    } catch {
        print("Failed to extract frame at \(time)s: \(error)")
    }
}
