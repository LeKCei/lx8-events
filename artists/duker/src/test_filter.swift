import AVFoundation
import Foundation
import CoreGraphics
import QuartzCore
import CoreImage
import AppKit

print("Testing CoreImage and CoreAnimation filter compilation on macOS...")

let layer = CALayer()
let filter = CIFilter(name: "CIColorControls")
if let filter = filter {
    filter.setDefaults()
    filter.setValue(0.0, forKey: kCIInputSaturationKey)
    layer.filters = [filter]
    print("Successfully created CIColorControls filter and applied it to CALayer.filters!")
} else {
    print("Failed to create CIColorControls filter")
}

let blurFilter = CIFilter(name: "CIGaussianBlur")
if let blurFilter = blurFilter {
    blurFilter.setDefaults()
    blurFilter.setValue(10.0, forKey: kCIInputRadiusKey)
    layer.filters?.append(blurFilter)
    print("Successfully created CIGaussianBlur filter and applied it to CALayer.filters!")
} else {
    print("Failed to create CIGaussianBlur filter")
}
