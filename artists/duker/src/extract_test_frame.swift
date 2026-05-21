import AVFoundation
import Foundation
import CoreGraphics
import ImageIO

let videoPath = "/Users/alexei.ferreira/Events/artists/gui-boratto/Final_Deliverables/Instagram_Stories_Reels_9_16/gui_boratto_event_story_neon.mp4"
let videoURL = URL(fileURLWithPath: videoPath)
let asset = AVAsset(url: videoURL)
let generator = AVAssetImageGenerator(asset: asset)
generator.appliesPreferredTrackTransform = true
generator.requestedTimeToleranceBefore = .zero
generator.requestedTimeToleranceAfter = .zero

let time = 5.0
let cmTime = CMTime(seconds: time, preferredTimescale: 600)
do {
    let cgImage = try generator.copyCGImage(at: cmTime, actualTime: nil)
    let outPath = "/Users/alexei.ferreira/.gemini/antigravity/brain/3251c28c-63f6-4664-adc4-19c8957f68de/test_frame_5s.jpg"
    let fileURL = URL(fileURLWithPath: outPath)
    
    guard let destination = CGImageDestinationCreateWithURL(fileURL as CFURL, kUTTypeJPEG, 1, nil) else {
        print("Failed to create image destination")
        exit(1)
    }
    
    let properties = [kCGImageDestinationLossyCompressionQuality: 0.85] as CFDictionary
    CGImageDestinationAddImage(destination, cgImage, properties)
    if CGImageDestinationFinalize(destination) {
        print("SUCCESS: Extracted frame at 5s to \(outPath)")
    } else {
        print("Failed to finalize image destination")
    }
} catch {
    print("Error extracting frame: \(error)")
}
