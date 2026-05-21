import AVFoundation
import Foundation

let videoURL = URL(fileURLWithPath: "/Users/alexei.ferreira/Events/guiboratto_post/VIDEO-2025-05-08-17-54-08.mp4")
let asset = AVAsset(url: videoURL)

let semaphore = DispatchSemaphore(value: 0)

asset.loadValuesAsynchronously(forKeys: ["tracks", "duration"]) {
    var error: NSError? = nil
    let status = asset.statusOfValue(forKey: "tracks", error: &error)
    if status == .loaded {
        print("Video Duration: \(CMTimeGetSeconds(asset.duration)) seconds")
        let videoTracks = asset.tracks(withMediaType: .video)
        print("Number of video tracks: \(videoTracks.count)")
        if let videoTrack = videoTracks.first {
            let size = videoTrack.naturalSize
            let transform = videoTrack.preferredTransform
            print("Track Size (natural): \(size.width) x \(size.height)")
            print("Preferred Transform: \(transform)")
            
            // Determine actual display size considering transform
            var displayWidth = size.width
            var displayHeight = size.height
            if (transform.b == 1.0 && transform.c == -1.0) || (transform.b == -1.0 && transform.c == 1.0) {
                displayWidth = size.height
                displayHeight = size.width
            }
            print("Actual Display Size: \(displayWidth) x \(displayHeight)")
            print("Nominal Frame Rate: \(videoTrack.nominalFrameRate) fps")
            print("Estimated Data Rate: \(videoTrack.estimatedDataRate / 1000000.0) Mbps")
        }
        
        let audioTracks = asset.tracks(withMediaType: .audio)
        print("Number of audio tracks: \(audioTracks.count)")
    } else {
        print("Failed to load tracks: \(error?.localizedDescription ?? "unknown error")")
    }
    semaphore.signal()
}

semaphore.wait()
