import AVFoundation
import Foundation
import CoreGraphics
import QuartzCore
import CoreImage
import AppKit

// Helper to dynamically resolve the artist directory based on executable path
func getArtistBasePath() -> String {
    let execPath = CommandLine.arguments[0]
    let execURL = URL(fileURLWithPath: execPath)
    
    // Go up two levels: from executable in src/ to parent gui-boratto/
    let srcURL = execURL.deletingLastPathComponent()
    let artistURL = srcURL.deletingLastPathComponent()
    
    let csvURL = artistURL.appendingPathComponent("tour_dates.csv")
    if FileManager.default.fileExists(atPath: csvURL.path) {
        return artistURL.path
    }
    
    // Fallback path
    return "/Users/alexei.ferreira/Events/artists/gui-boratto"
}

let artistBasePath = getArtistBasePath()

// Struct to store tour dates
struct TourDate {
    let date: String
    let venue: String
    let city: String
    let country: String
}

// Function to map country codes to full uppercase country names
func getFullCountryName(code: String) -> String {
    let mapping = [
        "BR": "BRAZIL",
        "AR": "ARGENTINA",
        "CH": "SWITZERLAND",
        "ES": "SPAIN",
        "PT": "PORTUGAL",
        "DE": "GERMANY",
        "GB": "U. KINGDOM",
        "MX": "MEXICO",
        "CO": "COLOMBIA",
        "FR": "FRANCE",
        "NL": "NETHERLANDS"
    ]
    return mapping[code.uppercased()] ?? code.uppercased()
}

// Simple CSV parser for tour dates
func parseTourDates() -> [TourDate] {
    var dates = [TourDate]()
    let csvPath = "\(artistBasePath)/tour_dates.csv"
    guard let content = try? String(contentsOfFile: csvPath, encoding: .utf8) else {
        print("Failed to read tour_dates.csv")
        return dates
    }
    
    let lines = content.components(separatedBy: .newlines)
    for line in lines {
        let trimmed = line.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty || trimmed.hasPrefix("#") { continue }
        
        let parts = trimmed.components(separatedBy: ",")
        if parts.count >= 4 {
            let date = parts[0].trimmingCharacters(in: .whitespaces)
            let venue = parts[1].trimmingCharacters(in: .whitespaces)
            let city = parts[2].trimmingCharacters(in: .whitespaces)
            let countryCode = parts[3].trimmingCharacters(in: .whitespaces)
            
            dates.append(TourDate(
                date: date,
                venue: venue,
                city: city,
                country: getFullCountryName(code: countryCode)
            ))
        }
    }
    return dates
}

// Helper to load CGImage from file path on macOS
func loadCGImage(path: String) -> CGImage? {
    guard let image = NSImage(contentsOfFile: path) else {
        print("Failed to load NSImage from \(path)")
        return nil
    }
    var imageRect = CGRect(x: 0, y: 0, width: image.size.width, height: image.size.height)
    return image.cgImage(forProposedRect: &imageRect, context: nil, hints: nil)
}

// Helper to create fade animation
func createFadeAnimation(begin: Double, duration: Double, from: Double, to: Double) -> CABasicAnimation {
    let anim = CABasicAnimation(keyPath: "opacity")
    anim.fromValue = from
    anim.toValue = to
    anim.duration = duration
    anim.beginTime = AVCoreAnimationBeginTimeAtZero + begin
    anim.fillMode = .both
    anim.isRemovedOnCompletion = false
    return anim
}

// Helper to create slide animation
func createSlideAnimation(begin: Double, duration: Double, fromY: CGFloat, toY: CGFloat) -> CABasicAnimation {
    let anim = CABasicAnimation(keyPath: "position.y")
    anim.fromValue = fromY
    anim.toValue = toY
    anim.duration = duration
    anim.beginTime = AVCoreAnimationBeginTimeAtZero + begin
    anim.fillMode = .both
    anim.isRemovedOnCompletion = false
    return anim
}

// Helper to create beat pulse animation (kick reactive transient pulse)
func createBeatPulseAnimation(baseScale: CGFloat, bpm: Double) -> CAKeyframeAnimation {
    let beatDuration = 60.0 / bpm
    let anim = CAKeyframeAnimation(keyPath: "transform.scale")
    anim.values = [
        baseScale,
        baseScale * 1.022,  // Subtle premium 2.2% scale punch
        baseScale * 1.004,  // Smooth decay
        baseScale           // Return to base
    ]
    anim.keyTimes = [0.0, 0.1, 0.4, 1.0] as [NSNumber]
    anim.duration = beatDuration
    anim.repeatCount = .infinity
    anim.beginTime = AVCoreAnimationBeginTimeAtZero
    anim.fillMode = .forwards
    anim.isRemovedOnCompletion = false
    return anim
}


// Parse Command Line Arguments
let arguments = CommandLine.arguments
if arguments.count < 4 {
    print("Usage: swift video_editor.swift [tour|event|tour_sa|tour_eu1|tour_eu2|tour_na] [story|post] [gradient|bokeh|glass]")
    exit(1)
}

let mode = arguments[1].lowercased()       // "tour", "event", or regional "tour_sa", "tour_eu1", "tour_eu2", "tour_na"
let allowedModes = ["tour", "event", "tour_sa", "tour_eu1", "tour_eu2", "tour_na"]
if !allowedModes.contains(mode) {
    print("Error: Invalid mode. Must be one of \(allowedModes)")
    exit(1)
}

let format = arguments[2].lowercased()     // "story" or "post"
if format != "story" && format != "post" {
    print("Error: Invalid format. Must be 'story' or 'post'")
    exit(1)
}

let style = arguments[3].lowercased()      // "gradient", "bokeh", "glass", "neon", or "minimal"
if style != "gradient" && style != "bokeh" && style != "glass" && style != "neon" && style != "minimal" {
    print("Error: Invalid style. Must be 'gradient', 'bokeh', 'glass', 'neon', or 'minimal'")
    exit(1)
}

print("Running video editor in '\(mode)' mode with '\(format)' format and '\(style)' style...")

let sourceVideoPath = "\(artistBasePath)/Sources_and_Assets/VIDEO-2025-05-08-17-54-08.mp4"

// Dynamic output path organization under Final_Deliverables
let outputFolder = format == "story" ? 
    "\(artistBasePath)/Final_Deliverables/Instagram_Stories_Reels_9_16" : 
    "\(artistBasePath)/Final_Deliverables/Instagram_Posts_4_5"

try? FileManager.default.createDirectory(atPath: outputFolder, withIntermediateDirectories: true, attributes: nil)

let outputVideoPath = "\(outputFolder)/gui_boratto_\(mode)_\(format)_\(style).mp4"

let sourceURL = URL(fileURLWithPath: sourceVideoPath)
let outputURL = URL(fileURLWithPath: outputVideoPath)

// Remove existing file if present
if FileManager.default.fileExists(atPath: outputVideoPath) {
    try? FileManager.default.removeItem(atPath: outputVideoPath)
    print("Removed existing file at \(outputVideoPath)")
}

let asset = AVAsset(url: sourceURL)
let composition = AVMutableComposition()

guard let videoTrack = asset.tracks(withMediaType: .video).first,
      let compositionVideoTrack = composition.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid) else {
    print("Error: Could not find or add video track")
    exit(1)
}

let timeRange = CMTimeRange(start: .zero, duration: asset.duration)
try compositionVideoTrack.insertTimeRange(timeRange, of: videoTrack, at: .zero)

// Preserving original high-fidelity audio
if let audioTrack = asset.tracks(withMediaType: .audio).first,
   let compositionAudioTrack = composition.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid) {
    try? compositionAudioTrack.insertTimeRange(timeRange, of: audioTrack, at: .zero)
    print("Preserved audio track successfully.")
} else {
    print("Warning: No audio track found or failed to insert.")
}

// Dimensions for Story (1080x1920) vs Post (1080x1350)
let videoSize = format == "story" ? CGSize(width: 1080, height: 1920) : CGSize(width: 1080, height: 1350)
print("Output video format size: \(videoSize.width) x \(videoSize.height)")

// CoreAnimation parent render layer
let parentLayer = CALayer()
parentLayer.frame = CGRect(x: 0, y: 0, width: videoSize.width, height: videoSize.height)
parentLayer.isGeometryFlipped = true

// Video track frame renderer layer
let videoLayer = CALayer()
videoLayer.frame = CGRect(x: 0, y: 0, width: videoSize.width, height: videoSize.height)

// CoreImage filters applied to the background video track layer (GPU Accelerated)
var activeFilters = [CIFilter]()

// 1. Gaussian Blur (Bokeh) style treatment
if style == "bokeh" {
    if let blurFilter = CIFilter(name: "CIGaussianBlur") {
        blurFilter.setDefaults()
        blurFilter.setValue(16.0, forKey: kCIInputRadiusKey) // Premium 16px soft blur
        activeFilters.append(blurFilter)
    }
    
    // Scale up the video layer by 8% to hide blurred black outer fringes (overscan)
    videoLayer.transform = CATransform3DMakeScale(1.08, 1.08, 1.0)
    videoLayer.anchorPoint = CGPoint(x: 0.5, y: 0.5)
    videoLayer.position = CGPoint(x: videoSize.width / 2.0, y: videoSize.height / 2.0)
} else if style == "neon" {
    // Cyberpunk electric saturation and contrast boost
    if let colorFilter = CIFilter(name: "CIColorControls") {
        colorFilter.setDefaults()
        colorFilter.setValue(1.4, forKey: kCIInputSaturationKey)
        colorFilter.setValue(1.12, forKey: kCIInputContrastKey)
        colorFilter.setValue(-0.05, forKey: kCIInputBrightnessKey)
        activeFilters.append(colorFilter)
    }
} else if style == "minimal" {
    // Minimalist vignette/dark tint desaturated tone
    if let colorFilter = CIFilter(name: "CIColorControls") {
        colorFilter.setDefaults()
        colorFilter.setValue(0.7, forKey: kCIInputSaturationKey) // Classy desaturation
        colorFilter.setValue(1.05, forKey: kCIInputContrastKey)
        activeFilters.append(colorFilter)
    }
}

if !activeFilters.isEmpty {
    videoLayer.filters = activeFilters
}

// Center-anchor background video track for seamless kick scaling pulse
videoLayer.anchorPoint = CGPoint(x: 0.5, y: 0.5)
videoLayer.position = CGPoint(x: videoSize.width / 2.0, y: videoSize.height / 2.0)
let baseVideoScale: CGFloat = (style == "bokeh") ? 1.08 : 1.0
let kickPulse = createBeatPulseAnimation(baseScale: baseVideoScale, bpm: 124.0)
videoLayer.add(kickPulse, forKey: "kickPulse")

// CoreAnimation overlays container

let overlayLayer = CALayer()
overlayLayer.frame = CGRect(x: 0, y: 0, width: videoSize.width, height: videoSize.height)

// Promo Container Layer for easy grouping and fading out at 14s
let promoContainer = CALayer()
promoContainer.frame = CGRect(x: 0, y: 0, width: videoSize.width, height: videoSize.height)

parentLayer.addSublayer(videoLayer)
parentLayer.addSublayer(overlayLayer)
overlayLayer.addSublayer(promoContainer)

// Load source graphic assets
let logoPath = "\(artistBasePath)/Sources_and_Assets/gui boratto logo.png"
let logoCGImage = loadCGImage(path: logoPath)

let sponsorDocPath = "\(artistBasePath)/Sources_and_Assets/DOC_AVATAR6.PNG"
let sponsorMetropolePath = "\(artistBasePath)/Sources_and_Assets/metropole logo.png"
let sponsorDukerPath = "\(artistBasePath)/Sources_and_Assets/dukermusic_logo_white.PNG"

let docCG = loadCGImage(path: sponsorDocPath)
let metropoleCG = loadCGImage(path: sponsorMetropolePath)
let dukerCG = loadCGImage(path: sponsorDukerPath)

// Typography font references
let fontBoldName = "HelveticaNeue-Bold"
let fontMediumName = "HelveticaNeue-Medium"
let fontRegularName = "HelveticaNeue"

// Apply overlay styling elements
if style == "gradient" {
    // Premium vertical gradient that fades to solid black at the bottom (Approved Poster Styling)
    let gradientLayer = CAGradientLayer()
    gradientLayer.frame = CGRect(x: 0, y: 0, width: videoSize.width, height: videoSize.height)
    gradientLayer.colors = [
        CGColor(red: 0, green: 0, blue: 0, alpha: 0.0),
        CGColor(red: 0, green: 0, blue: 0, alpha: 0.95)
    ]
    
    if format == "story" {
        gradientLayer.startPoint = CGPoint(x: 0.5, y: 0.72)
        gradientLayer.endPoint = CGPoint(x: 0.5, y: 0.15)
    } else {
        gradientLayer.startPoint = CGPoint(x: 0.5, y: 0.78)
        gradientLayer.endPoint = CGPoint(x: 0.5, y: 0.18)
    }
    overlayLayer.addSublayer(gradientLayer)
    
} else if style == "glass" {
    // Aesthetic, highly transparent frosted glass card
    let cardLayer = CALayer()
    if format == "story" {
        if mode.hasPrefix("tour") {
            cardLayer.frame = CGRect(x: 80, y: 360, width: 920, height: 1220)
        } else {
            cardLayer.frame = CGRect(x: 80, y: 380, width: 920, height: 1180)
        }
    } else {
        if mode.hasPrefix("tour") {
            cardLayer.frame = CGRect(x: 80, y: 170, width: 920, height: 1010)
        } else {
            cardLayer.frame = CGRect(x: 80, y: 180, width: 920, height: 970)
        }
    }
    cardLayer.backgroundColor = CGColor(red: 0, green: 0, blue: 0, alpha: 0.55) // Frosted glass with excellent contrast
    cardLayer.cornerRadius = 24
    cardLayer.borderColor = CGColor(red: 1, green: 1, blue: 1, alpha: 0.25) // Thin white border
    cardLayer.borderWidth = 1.0
    promoContainer.addSublayer(cardLayer)
} else if style == "neon" {
    // Cyberpunk/electric neon card outline with drop glow
    let cardLayer = CALayer()
    if format == "story" {
        if mode.hasPrefix("tour") {
            cardLayer.frame = CGRect(x: 80, y: 360, width: 920, height: 1220)
        } else {
            cardLayer.frame = CGRect(x: 80, y: 380, width: 920, height: 1180)
        }
    } else {
        if mode.hasPrefix("tour") {
            cardLayer.frame = CGRect(x: 80, y: 170, width: 920, height: 1010)
        } else {
            cardLayer.frame = CGRect(x: 80, y: 180, width: 920, height: 970)
        }
    }
    cardLayer.backgroundColor = CGColor(red: 0, green: 0, blue: 0, alpha: 0.75) // Dark high-contrast backing
    cardLayer.cornerRadius = 24
    cardLayer.borderColor = CGColor(red: 0, green: 0.95, blue: 1.0, alpha: 0.8) // Electric cyan border
    cardLayer.borderWidth = 1.5
    
    // Ambient neon outer glow shadow
    cardLayer.shadowColor = CGColor(red: 0, green: 0.95, blue: 1.0, alpha: 1.0)
    cardLayer.shadowOpacity = 0.4
    cardLayer.shadowRadius = 8.0
    cardLayer.shadowOffset = .zero
    promoContainer.addSublayer(cardLayer)
} else if style == "minimal" {
    // Clean modern minimalist hairline card
    let cardLayer = CALayer()
    if format == "story" {
        if mode.hasPrefix("tour") {
            cardLayer.frame = CGRect(x: 80, y: 360, width: 920, height: 1220)
        } else {
            cardLayer.frame = CGRect(x: 80, y: 380, width: 920, height: 1180)
        }
    } else {
        if mode.hasPrefix("tour") {
            cardLayer.frame = CGRect(x: 80, y: 170, width: 920, height: 1010)
        } else {
            cardLayer.frame = CGRect(x: 80, y: 180, width: 920, height: 970)
        }
    }
    cardLayer.backgroundColor = CGColor(red: 0, green: 0, blue: 0, alpha: 0.4) // Subtle elegant translucent tint
    cardLayer.cornerRadius = 12 // Modern sleek sharp corners
    cardLayer.borderColor = CGColor(red: 1, green: 1, blue: 1, alpha: 0.15) // Hairline subtle border
    cardLayer.borderWidth = 0.5
    promoContainer.addSublayer(cardLayer)
}

if mode.hasPrefix("tour") {
    // ==========================================
    // TOUR DATES PROMO (WITH SAFE ZONE COMPLIANCE)
    // ==========================================
    
    // 1. Center placed Artist Logo
    if let logo = logoCGImage {
        let logoLayer = CALayer()
        let logoW: CGFloat = format == "story" ? 940 : 900
        let logoH: CGFloat = format == "story" ? 80 : 76
        let logoY: CGFloat = format == "story" ? 340 : 194
        logoLayer.frame = CGRect(x: (videoSize.width - logoW) / 2.0, y: logoY, width: logoW, height: logoH)
        logoLayer.contents = logo
        promoContainer.addSublayer(logoLayer)
    }
    
    // 2. Tracked Subheader "NEXT DATES"
    let subLayer = CATextLayer()
    let subY: CGFloat = format == "story" ? 490 : 310
    let subSize: CGFloat = format == "story" ? 28 : 22
    subLayer.frame = CGRect(x: 80, y: subY, width: 920, height: 40)
    subLayer.string = "N E X T   D A T E S"
    subLayer.font = NSFont(name: fontBoldName, size: subSize) ?? NSFont.boldSystemFont(ofSize: subSize)
    subLayer.fontSize = subSize
    subLayer.foregroundColor = CGColor(red: 0.7, green: 0.7, blue: 0.7, alpha: 1)
    subLayer.alignmentMode = .center
    subLayer.contentsScale = 2.0
    promoContainer.addSublayer(subLayer)
    
    var tourDates = parseTourDates()
    
    // Filter regional sub-campaign modes
    if mode == "tour_sa" {
        tourDates = tourDates.filter { $0.country == "BRAZIL" || $0.country == "ARGENTINA" }
    } else if mode == "tour_eu1" {
        tourDates = tourDates.filter { $0.city == "BASEL" || $0.city == "IBIZA" || $0.city == "LISBON" || $0.city == "COSTA DA CAPARICA" }
    } else if mode == "tour_eu2" {
        tourDates = tourDates.filter { $0.city == "BARCELONA" || $0.city == "ZURICH" || $0.city == "MUNICH" || $0.city == "LONDON" || $0.city == "PARIS" || $0.city == "AMSTERDAM" }
    } else if mode == "tour_na" {
        tourDates = tourDates.filter { $0.country == "MEXICO" || $0.country == "COLOMBIA" }
    }
    
    print("Parsed and filtered \(tourDates.count) tour dates for rendering.")
    
    if style == "bokeh" {
        // KINETIC BLUR ANIMAION (Group transitions optimized to end at 14.0s)
        let isRegional = mode.hasPrefix("tour_") && mode != "tour"
        
        let groups: [(CountableRange<Int>, Double, Double)]
        if isRegional {
            groups = [
                (0..<tourDates.count, 0.0, 14.0)
            ]
        } else {
            groups = [
                (0..<4, 0.0, 3.5),
                (4..<8, 3.5, 7.0),
                (8..<12, 7.0, 10.5),
                (12..<16, 10.5, 14.0)
            ]
        }
        
        for (_, (range, startSec, endSec)) in groups.enumerated() {
            let groupContainer = CALayer()
            groupContainer.frame = CGRect(x: 0, y: 0, width: videoSize.width, height: videoSize.height)
            groupContainer.opacity = 0.0
            
            let fadeIn = createFadeAnimation(begin: startSec, duration: 0.4, from: 0.0, to: 1.0)
            groupContainer.add(fadeIn, forKey: "fadeIn")
            
            if endSec < 14.0 {
                let fadeOut = createFadeAnimation(begin: endSec - 0.4, duration: 0.4, from: 1.0, to: 0.0)
                groupContainer.add(fadeOut, forKey: "fadeOut")
            } else {
                groupContainer.opacity = 1.0
            }
            
            let visibleCount = range.clamped(to: 0..<tourDates.count).count
            let rowHeight: CGFloat
            let gridTopAnim: CGFloat
            if format == "story" {
                rowHeight = visibleCount > 4 ? 120 : 160
                gridTopAnim = visibleCount > 4 ? 550 : 560
            } else {
                rowHeight = visibleCount > 4 ? 90 : 120
                gridTopAnim = visibleCount > 4 ? 440 : 430
            }
            
            for (idx, i) in range.enumerated() {
                if i >= tourDates.count { break }
                let td = tourDates[i]
                let rowY = gridTopAnim + CGFloat(idx) * rowHeight
                
                // Bold combined Date/City header
                let dateLayer = CATextLayer()
                let dateSizeAnim: CGFloat = format == "story" ? 34 : 26
                let venueSizeAnim: CGFloat = format == "story" ? 24 : 18
                
                let dateYOffset: CGFloat
                let venueYOffset: CGFloat
                if format == "story" {
                    if visibleCount > 4 {
                        dateYOffset = 20
                        venueYOffset = 65
                    } else {
                        dateYOffset = 40
                        venueYOffset = 85
                    }
                } else {
                    if visibleCount > 4 {
                        dateYOffset = 5
                        venueYOffset = 50
                    } else {
                        dateYOffset = 20
                        venueYOffset = 65
                    }
                }
                
                dateLayer.frame = CGRect(x: 40, y: rowY + dateYOffset, width: videoSize.width - 80, height: 40)
                dateLayer.string = "\(td.date.uppercased())  \(td.city.uppercased()), \(td.country)"
                dateLayer.font = NSFont(name: fontBoldName, size: dateSizeAnim) ?? NSFont.boldSystemFont(ofSize: dateSizeAnim)
                dateLayer.fontSize = dateSizeAnim
                dateLayer.foregroundColor = CGColor.white
                dateLayer.alignmentMode = .center
                dateLayer.contentsScale = 2.0
                groupContainer.addSublayer(dateLayer)
                
                // Venue details centered below
                let venueLayer = CATextLayer()
                venueLayer.frame = CGRect(x: 40, y: rowY + venueYOffset, width: videoSize.width - 80, height: 35)
                venueLayer.string = td.venue.uppercased()
                venueLayer.font = NSFont(name: fontRegularName, size: venueSizeAnim) ?? NSFont.systemFont(ofSize: venueSizeAnim)
                venueLayer.fontSize = venueSizeAnim
                venueLayer.foregroundColor = CGColor(red: 0.75, green: 0.75, blue: 0.75, alpha: 1)
                venueLayer.alignmentMode = .center
                venueLayer.contentsScale = 2.0
                groupContainer.addSublayer(venueLayer)
            }
            
            promoContainer.addSublayer(groupContainer)
        }
        
    } else {
        // STATIC 3-COLUMN TABLE SYSTEM (Clean, Spacious, No-Overlap Layout)
        let isRegional = mode.hasPrefix("tour_") && mode != "tour"
        
        // Filter/limit the static display of dates to prevent vertical crowding
        // We will show at most 7 dates and show a beautifully aligned website footer
        let maxVisibleDates = 7
        let visibleDates = Array(tourDates.prefix(maxVisibleDates))
        let showMoreFooter = tourDates.count > maxVisibleDates
        
        let rowHeight: CGFloat = format == "story" ? 65 : 48
        let gridTop_new: CGFloat
        if isRegional {
            let totalTableHeight = CGFloat(visibleDates.count) * rowHeight + (showMoreFooter ? rowHeight : 0)
            let availableHeight = format == "story" ? (1310.0 - 500.0) : (940.0 - 340.0)
            let baseGridTop = format == "story" ? 1310.0 : 940.0
            let gridTop_old = baseGridTop - (availableHeight - totalTableHeight) / 2.0
            gridTop_new = videoSize.height - gridTop_old - rowHeight
        } else {
            gridTop_new = format == "story" ? 545 : 362
        }
        
        let fontSize: CGFloat = format == "story" ? 22 : 18
        
        for (i, td) in visibleDates.enumerated() {
            let rowY = gridTop_new + CGFloat(i) * rowHeight
            
            // 1. Date Column (Bold, left-aligned)
            let dateColLayer = CATextLayer()
            dateColLayer.frame = CGRect(x: 100, y: rowY, width: 140, height: rowHeight)
            dateColLayer.string = td.date.uppercased()
            dateColLayer.font = NSFont(name: fontBoldName, size: fontSize) ?? NSFont.boldSystemFont(ofSize: fontSize)
            dateColLayer.fontSize = fontSize
            dateColLayer.foregroundColor = CGColor.white
            dateColLayer.alignmentMode = .left
            dateColLayer.contentsScale = 2.0
            promoContainer.addSublayer(dateColLayer)
            
            // 2. Venue Column (Bold, left-aligned, truncated with ellipses if too long)
            let venueColLayer = CATextLayer()
            venueColLayer.frame = CGRect(x: 260, y: rowY, width: 420, height: rowHeight)
            venueColLayer.string = td.venue.uppercased()
            venueColLayer.font = NSFont(name: fontBoldName, size: fontSize) ?? NSFont.boldSystemFont(ofSize: fontSize)
            venueColLayer.fontSize = fontSize
            venueColLayer.foregroundColor = CGColor.white
            venueColLayer.alignmentMode = .left
            venueColLayer.truncationMode = .end
            venueColLayer.contentsScale = 2.0
            promoContainer.addSublayer(venueColLayer)
            
            // 3. Location Column (Regular, right-aligned)
            let locationColLayer = CATextLayer()
            locationColLayer.frame = CGRect(x: 700, y: rowY, width: 280, height: rowHeight)
            let locationString = "\(td.city.uppercased()), \(td.country.uppercased())"
            locationColLayer.string = locationString
            locationColLayer.font = NSFont(name: fontRegularName, size: fontSize) ?? NSFont.systemFont(ofSize: fontSize)
            locationColLayer.fontSize = fontSize
            locationColLayer.foregroundColor = CGColor(red: 0.75, green: 0.75, blue: 0.75, alpha: 1)
            locationColLayer.alignmentMode = .right
            locationColLayer.contentsScale = 2.0
            promoContainer.addSublayer(locationColLayer)
        }
        
        // 4. Redirection Footer (Guides users to view the rest of the dates online)
        if showMoreFooter {
            let footerY = gridTop_new + CGFloat(visibleDates.count) * rowHeight + 20
            let footerLayer = CATextLayer()
            let footerFontSize = fontSize - 2
            footerLayer.frame = CGRect(x: 100, y: footerY, width: 880, height: rowHeight)
            footerLayer.string = "+ MORE DATES & TICKETS AT WWW.GUIBORATTO.COM"
            footerLayer.font = NSFont(name: fontMediumName, size: footerFontSize) ?? NSFont.systemFont(ofSize: footerFontSize)
            footerLayer.fontSize = footerFontSize
            footerLayer.foregroundColor = CGColor(red: 0.9, green: 0.9, blue: 0.9, alpha: 1)
            footerLayer.alignmentMode = .center
            footerLayer.contentsScale = 2.0
            promoContainer.addSublayer(footerLayer)
        }
    }
    
    // 3. Center Aligned Sponsor Logos at bottom
    let sponsorY: CGFloat = format == "story" ? 1484 : 1130
    let sponsorH: CGFloat = format == "story" ? 36 : 30
    let gap: CGFloat = format == "story" ? 40 : 30
    
    let docW = sponsorH * 2.0
    let metropoleW = sponsorH * 3.0
    let dukerW = sponsorH * 2.25
    let totalSponsorsW = docW + metropoleW + dukerW + (2 * gap)
    let startSponsorX = (videoSize.width - totalSponsorsW) / 2.0
    
    // Premium dark translucent backing container pill for extreme legibility and visibility
    let backingLayer = CALayer()
    let paddingX: CGFloat = 36
    let paddingY: CGFloat = 12
    backingLayer.frame = CGRect(
        x: startSponsorX - paddingX,
        y: sponsorY - paddingY,
        width: totalSponsorsW + (2 * paddingX),
        height: sponsorH + (2 * paddingY)
    )
    backingLayer.backgroundColor = CGColor(red: 0, green: 0, blue: 0, alpha: 0.65) // Dark high-contrast backing
    backingLayer.cornerRadius = (sponsorH + (2 * paddingY)) / 2.0
    backingLayer.borderColor = CGColor(red: 1, green: 1, blue: 1, alpha: 0.15)
    backingLayer.borderWidth = 1.0
    promoContainer.addSublayer(backingLayer)
    
    if let doc = docCG {
        let l = CALayer()
        l.frame = CGRect(x: startSponsorX, y: sponsorY, width: docW, height: sponsorH)
        l.contents = doc
        promoContainer.addSublayer(l)
    }
    if let metropole = metropoleCG {
        let l = CALayer()
        l.frame = CGRect(x: startSponsorX + docW + gap, y: sponsorY, width: metropoleW, height: sponsorH)
        l.contents = metropole
        promoContainer.addSublayer(l)
    }
    if let duker = dukerCG {
        let l = CALayer()
        l.frame = CGRect(x: startSponsorX + docW + metropoleW + (2 * gap), y: sponsorY, width: dukerW, height: sponsorH)
        l.contents = duker
        promoContainer.addSublayer(l)
    }
    
} else {
    // ==========================================
    // BARCELONA EVENT GIG PROMO (SAFE ZONE ENFORCED)
    // ==========================================
    
    // 1. Presents header
    let presentsLayer = CATextLayer()
    let presY: CGFloat = format == "story" ? 360 : 200
    let presSize: CGFloat = format == "story" ? 24 : 20
    presentsLayer.frame = CGRect(x: 80, y: presY, width: 920, height: 40)
    presentsLayer.string = "D Ü K E R   M U S I C   P R E S E N T S"
    presentsLayer.font = NSFont(name: fontBoldName, size: presSize) ?? NSFont.boldSystemFont(ofSize: presSize)
    presentsLayer.fontSize = presSize
    presentsLayer.foregroundColor = CGColor(red: 0.8, green: 0.8, blue: 0.8, alpha: 1)
    presentsLayer.alignmentMode = .center
    presentsLayer.contentsScale = 2.0
    promoContainer.addSublayer(presentsLayer)
    
    // 2. Artist logo
    let logoLayer = CALayer()
    let logoW: CGFloat = format == "story" ? 600 : 500
    let logoH: CGFloat = format == "story" ? 96 : 80
    let logoY: CGFloat = format == "story" ? 544 : 330
    if let logo = logoCGImage {
        logoLayer.frame = CGRect(x: (videoSize.width - logoW) / 2.0, y: logoY, width: logoW, height: logoH)
        logoLayer.contents = logo
        promoContainer.addSublayer(logoLayer)
    }
    
    // 3. Show Date
    let dateLayer = CATextLayer()
    let dateY: CGFloat = format == "story" ? 760 : 500
    let dateSize: CGFloat = format == "story" ? 42 : 34
    dateLayer.frame = CGRect(x: 80, y: dateY, width: 920, height: 60)
    dateLayer.string = "THURSDAY, 25 JUNE 2026"
    dateLayer.font = NSFont(name: fontBoldName, size: dateSize) ?? NSFont.boldSystemFont(ofSize: dateSize)
    dateLayer.fontSize = dateSize
    dateLayer.foregroundColor = CGColor.white
    dateLayer.alignmentMode = .center
    dateLayer.contentsScale = 2.0
    promoContainer.addSublayer(dateLayer)
    
    // 4. Time details
    let timeLayer = CATextLayer()
    let timeY: CGFloat = format == "story" ? 860 : 590
    let timeSize: CGFloat = format == "story" ? 28 : 22
    timeLayer.frame = CGRect(x: 80, y: timeY, width: 920, height: 50)
    timeLayer.string = "DOORS OPEN 23:59"
    timeLayer.font = NSFont(name: fontMediumName, size: timeSize) ?? NSFont.systemFont(ofSize: timeSize)
    timeLayer.fontSize = timeSize
    timeLayer.foregroundColor = CGColor(red: 0.7, green: 0.7, blue: 0.7, alpha: 1)
    timeLayer.alignmentMode = .center
    timeLayer.contentsScale = 2.0
    promoContainer.addSublayer(timeLayer)
    
    // 5. Venue name
    let venueLayer = CATextLayer()
    let venY: CGFloat = format == "story" ? 1030 : 710
    let venSize: CGFloat = format == "story" ? 54 : 44
    venueLayer.frame = CGRect(x: 80, y: venY, width: 920, height: 70)
    venueLayer.string = "MACARENA CLUB"
    venueLayer.font = NSFont(name: fontBoldName, size: venSize) ?? NSFont.boldSystemFont(ofSize: venSize)
    venueLayer.fontSize = venSize
    venueLayer.foregroundColor = CGColor.white
    venueLayer.alignmentMode = .center
    venueLayer.contentsScale = 2.0
    promoContainer.addSublayer(venueLayer)
    
    // 6. City & Country
    let cityLayer = CATextLayer()
    let cityY: CGFloat = format == "story" ? 1140 : 810
    let citySize: CGFloat = format == "story" ? 36 : 30
    cityLayer.frame = CGRect(x: 80, y: cityY, width: 920, height: 50)
    cityLayer.string = "BARCELONA, SPAIN"
    cityLayer.font = NSFont(name: fontBoldName, size: citySize) ?? NSFont.boldSystemFont(ofSize: citySize)
    cityLayer.fontSize = citySize
    cityLayer.foregroundColor = CGColor.white
    cityLayer.alignmentMode = .center
    cityLayer.contentsScale = 2.0
    promoContainer.addSublayer(cityLayer)
    
    // 7. Address
    let addressLayer = CATextLayer()
    let addrY: CGFloat = format == "story" ? 1230 : 890
    let addrSize: CGFloat = format == "story" ? 23 : 18
    addressLayer.frame = CGRect(x: 80, y: addrY, width: 920, height: 40)
    addressLayer.string = "CARRER NOU DE SAN FRANCESC, 5"
    addressLayer.font = NSFont(name: fontRegularName, size: addrSize) ?? NSFont.systemFont(ofSize: addrSize)
    addressLayer.fontSize = addrSize
    addressLayer.foregroundColor = CGColor(red: 0.65, green: 0.65, blue: 0.65, alpha: 1)
    addressLayer.alignmentMode = .center
    addressLayer.contentsScale = 2.0
    promoContainer.addSublayer(addressLayer)
    
    // 8. Sponsor Logos at bottom
    let docLayer = CALayer()
    let metropoleLayer = CALayer()
    let dukerLayer = CALayer()
    let backingLayer = CALayer()
    let sponsorY: CGFloat = format == "story" ? 1464 : 1120
    let sponsorH: CGFloat = format == "story" ? 36 : 30
    let gap: CGFloat = format == "story" ? 40 : 30
    
    let docW = sponsorH * 2.0
    let metropoleW = sponsorH * 3.0
    let dukerW = sponsorH * 2.25
    let totalSponsorsW = docW + metropoleW + dukerW + (2 * gap)
    let startSponsorX = (videoSize.width - totalSponsorsW) / 2.0
    
    // Premium dark translucent backing container pill for extreme legibility and visibility
    let paddingX: CGFloat = 36
    let paddingY: CGFloat = 12
    backingLayer.frame = CGRect(
        x: startSponsorX - paddingX,
        y: sponsorY - paddingY,
        width: totalSponsorsW + (2 * paddingX),
        height: sponsorH + (2 * paddingY)
    )
    backingLayer.backgroundColor = CGColor(red: 0, green: 0, blue: 0, alpha: 0.65) // Dark high-contrast backing
    backingLayer.cornerRadius = (sponsorH + (2 * paddingY)) / 2.0
    backingLayer.borderColor = CGColor(red: 1, green: 1, blue: 1, alpha: 0.15)
    backingLayer.borderWidth = 1.0
    promoContainer.addSublayer(backingLayer)
    
    if let doc = docCG {
        docLayer.frame = CGRect(x: startSponsorX, y: sponsorY, width: docW, height: sponsorH)
        docLayer.contents = doc
        promoContainer.addSublayer(docLayer)
    }
    if let metropole = metropoleCG {
        metropoleLayer.frame = CGRect(x: startSponsorX + docW + gap, y: sponsorY, width: metropoleW, height: sponsorH)
        metropoleLayer.contents = metropole
        promoContainer.addSublayer(metropoleLayer)
    }
    if let duker = dukerCG {
        dukerLayer.frame = CGRect(x: startSponsorX + docW + metropoleW + (2 * gap), y: sponsorY, width: dukerW, height: sponsorH)
        dukerLayer.contents = duker
        promoContainer.addSublayer(dukerLayer)
    }
    
    // Dynamic Kinetic entry reveals (Now applied to ALL video styles for maximum engagement!)
    if true {
        presentsLayer.opacity = 0.0
        logoLayer.opacity = 0.0
        dateLayer.opacity = 0.0
        timeLayer.opacity = 0.0
        venueLayer.opacity = 0.0
        cityLayer.opacity = 0.0
        addressLayer.opacity = 0.0
        docLayer.opacity = 0.0
        metropoleLayer.opacity = 0.0
        dukerLayer.opacity = 0.0
        backingLayer.opacity = 0.0
        
        // 1. Show the Artist Logo first ("Guiboratto")
        let logoMidY = logoY + logoH / 2.0
        logoLayer.add(createFadeAnimation(begin: 0.5, duration: 0.6, from: 0, to: 1), forKey: "fade")
        logoLayer.add(createSlideAnimation(begin: 0.5, duration: 0.6, fromY: logoMidY + 40, toY: logoMidY), forKey: "slide")
        
        // 2. Presents Header reveals second
        presentsLayer.add(createFadeAnimation(begin: 1.2, duration: 0.5, from: 0, to: 1), forKey: "fade")
        
        // 3. Show Date
        let dateMidY = dateY + 60.0 / 2.0
        dateLayer.add(createFadeAnimation(begin: 1.8, duration: 0.5, from: 0, to: 1), forKey: "fade")
        dateLayer.add(createSlideAnimation(begin: 1.8, duration: 0.5, fromY: dateMidY + 30, toY: dateMidY), forKey: "slide")
        
        // 4. Time Details
        let timeMidY = timeY + 50.0 / 2.0
        timeLayer.add(createFadeAnimation(begin: 2.2, duration: 0.5, from: 0, to: 1), forKey: "fade")
        timeLayer.add(createSlideAnimation(begin: 2.2, duration: 0.5, fromY: timeMidY + 30, toY: timeMidY), forKey: "slide")
        
        // 5. Venue Name
        let venMidY = venY + 70.0 / 2.0
        venueLayer.add(createFadeAnimation(begin: 2.8, duration: 0.5, from: 0, to: 1), forKey: "fade")
        venueLayer.add(createSlideAnimation(begin: 2.8, duration: 0.5, fromY: venMidY + 40, toY: venMidY), forKey: "slide")
        
        // 6. City & Country
        let cityMidY = cityY + 50.0 / 2.0
        cityLayer.add(createFadeAnimation(begin: 3.2, duration: 0.5, from: 0, to: 1), forKey: "fade")
        cityLayer.add(createSlideAnimation(begin: 3.2, duration: 0.5, fromY: cityMidY + 30, toY: cityMidY), forKey: "slide")
        
        // 7. Address
        addressLayer.add(createFadeAnimation(begin: 3.6, duration: 0.5, from: 0, to: 1), forKey: "fade")
        
        // 8. Sponsor Backing container pill fades in right before individual logos
        backingLayer.add(createFadeAnimation(begin: 4.0, duration: 0.4, from: 0, to: 1), forKey: "fade")
        
        // 9. Individual sponsor logos fade in sequentially
        docLayer.add(createFadeAnimation(begin: 4.3, duration: 0.5, from: 0, to: 1), forKey: "fade")
        metropoleLayer.add(createFadeAnimation(begin: 4.5, duration: 0.5, from: 0, to: 1), forKey: "fade")
        dukerLayer.add(createFadeAnimation(begin: 4.7, duration: 0.5, from: 0, to: 1), forKey: "fade")
    }
}

// ==========================================
// FINAL CTA SLATE (FADES IN AT 14.5s)
// ==========================================
let ctaContainer = CALayer()
ctaContainer.frame = CGRect(x: 0, y: 0, width: videoSize.width, height: videoSize.height)
ctaContainer.opacity = 0.0
overlayLayer.addSublayer(ctaContainer)

// Animate Promo Container to fade out from 14.0s to 14.5s
let promoFadeOut = CABasicAnimation(keyPath: "opacity")
promoFadeOut.fromValue = 1.0
promoFadeOut.toValue = 0.0
promoFadeOut.duration = 0.5
promoFadeOut.beginTime = AVCoreAnimationBeginTimeAtZero + 14.0
promoFadeOut.fillMode = .both
promoFadeOut.isRemovedOnCompletion = false
promoContainer.add(promoFadeOut, forKey: "fadeOut")

// Animate CTA Container to fade in from 14.5s to 15.0s
let ctaFadeIn = CABasicAnimation(keyPath: "opacity")
ctaFadeIn.fromValue = 0.0
ctaFadeIn.toValue = 1.0
ctaFadeIn.duration = 0.5
ctaFadeIn.beginTime = AVCoreAnimationBeginTimeAtZero + 14.5
ctaFadeIn.fillMode = .both
ctaFadeIn.isRemovedOnCompletion = false
ctaContainer.add(ctaFadeIn, forKey: "fadeIn")

// Build CTA frosted glass background card
if style == "glass" {
    let ctaCard = CALayer()
    if format == "story" {
        ctaCard.frame = CGRect(x: 80, y: 720, width: 920, height: 600)
    } else {
        ctaCard.frame = CGRect(x: 80, y: 450, width: 920, height: 550)
    }
    ctaCard.backgroundColor = CGColor(red: 0, green: 0, blue: 0, alpha: 0.55)
    ctaCard.cornerRadius = 24
    ctaCard.borderColor = CGColor(red: 1, green: 1, blue: 1, alpha: 0.25)
    ctaCard.borderWidth = 1.0
    ctaContainer.addSublayer(ctaCard)
} else if style == "neon" {
    let ctaCard = CALayer()
    if format == "story" {
        ctaCard.frame = CGRect(x: 80, y: 720, width: 920, height: 600)
    } else {
        ctaCard.frame = CGRect(x: 80, y: 450, width: 920, height: 550)
    }
    ctaCard.backgroundColor = CGColor(red: 0, green: 0, blue: 0, alpha: 0.75)
    ctaCard.cornerRadius = 24
    ctaCard.borderColor = CGColor(red: 0, green: 0.95, blue: 1.0, alpha: 0.8)
    ctaCard.borderWidth = 1.5
    ctaCard.shadowColor = CGColor(red: 0, green: 0.95, blue: 1.0, alpha: 1.0)
    ctaCard.shadowOpacity = 0.4
    ctaCard.shadowRadius = 8.0
    ctaCard.shadowOffset = .zero
    ctaContainer.addSublayer(ctaCard)
} else if style == "minimal" {
    let ctaCard = CALayer()
    if format == "story" {
        ctaCard.frame = CGRect(x: 80, y: 720, width: 920, height: 600)
    } else {
        ctaCard.frame = CGRect(x: 80, y: 450, width: 920, height: 550)
    }
    ctaCard.backgroundColor = CGColor(red: 0, green: 0, blue: 0, alpha: 0.4)
    ctaCard.cornerRadius = 12
    ctaCard.borderColor = CGColor(red: 1, green: 1, blue: 1, alpha: 0.15)
    ctaCard.borderWidth = 0.5
    ctaContainer.addSublayer(ctaCard)
}

// Centered artist logo on CTA slate
if let logo = logoCGImage {
    let logoLayer = CALayer()
    let logoW: CGFloat = format == "story" ? 600 : 500
    let logoH: CGFloat = format == "story" ? 51 : 42
    let logoY: CGFloat = format == "story" ? 829 : 528
    logoLayer.frame = CGRect(x: (videoSize.width - logoW) / 2.0, y: logoY, width: logoW, height: logoH)
    logoLayer.contents = logo
    ctaContainer.addSublayer(logoLayer)
}

// Bold primary text: "TICKETS ON SALE NOW"
let line1 = CATextLayer()
let l1Size: CGFloat = format == "story" ? 50 : 40
let l1Y: CGFloat = format == "story" ? 960 : 650
line1.frame = CGRect(x: 80, y: l1Y, width: 920, height: 80)
line1.string = "TICKETS ON SALE NOW"
line1.font = NSFont(name: fontBoldName, size: l1Size) ?? NSFont.boldSystemFont(ofSize: l1Size)
line1.fontSize = l1Size
line1.foregroundColor = CGColor.white
line1.alignmentMode = .center
line1.contentsScale = 2.0
ctaContainer.addSublayer(line1)

// Secondary tracked text: "LINK IN BIO"
let line2 = CATextLayer()
let l2Size: CGFloat = format == "story" ? 36 : 30
let l2Y: CGFloat = format == "story" ? 1100 : 790
line2.frame = CGRect(x: 80, y: l2Y, width: 920, height: 60)
line2.string = "L I N K   I N   B I O"
line2.font = NSFont(name: fontMediumName, size: l2Size) ?? NSFont.systemFont(ofSize: l2Size)
line2.fontSize = l2Size
line2.foregroundColor = CGColor(red: 0.8, green: 0.8, blue: 0.8, alpha: 1)
line2.alignmentMode = .center
line2.contentsScale = 2.0
ctaContainer.addSublayer(line2)

// Force layout and rasterization of layers for headless context
CATransaction.begin()
CATransaction.setValue(kCFBooleanTrue, forKey: kCATransactionDisableActions)
parentLayer.setNeedsLayout()
parentLayer.layoutIfNeeded()
parentLayer.setNeedsDisplay()
parentLayer.displayIfNeeded()
// Recursively force display and layout on all sublayers to ensure text and card overlays are fully rasterized
func forceRender(layer: CALayer) {
    layer.setNeedsLayout()
    layer.layoutIfNeeded()
    layer.setNeedsDisplay()
    layer.displayIfNeeded()
    if let sublayers = layer.sublayers {
        for sub in sublayers {
            forceRender(layer: sub)
        }
    }
}
forceRender(layer: parentLayer)
CATransaction.commit()
CATransaction.flush()

// Construct the Video Composition
let videoComposition = AVMutableVideoComposition()
videoComposition.renderSize = videoSize
videoComposition.frameDuration = CMTime(value: 1, timescale: 30) // Constant 30 fps
videoComposition.animationTool = AVVideoCompositionCoreAnimationTool(postProcessingAsVideoLayer: videoLayer, in: parentLayer)

let instruction = AVMutableVideoCompositionInstruction()
instruction.timeRange = CMTimeRange(start: .zero, duration: asset.duration)

let layerInstruction = AVMutableVideoCompositionLayerInstruction(assetTrack: compositionVideoTrack)

// Apply center crop transform for 4:5 format
if format == "post" {
    // The source is 1080x1920, target is 1080x1350. 
    // Shift the source down by 285px to center crop it vertically.
    let cropTransform = CGAffineTransform(translationX: 0, y: -285)
    layerInstruction.setTransform(cropTransform, at: .zero)
} else {
    layerInstruction.setTransform(videoTrack.preferredTransform, at: .zero)
}

instruction.layerInstructions = [layerInstruction]
videoComposition.instructions = [instruction]
videoComposition.renderScale = 1.0

// Setup AVAssetExportSession
guard let exportSession = AVAssetExportSession(asset: composition, presetName: AVAssetExportPresetHighestQuality) else {
    print("Error: Could not create AVAssetExportSession")
    exit(1)
}

exportSession.videoComposition = videoComposition
exportSession.outputURL = outputURL
exportSession.outputFileType = .mp4
exportSession.shouldOptimizeForNetworkUse = true

print("Starting video export to \(outputVideoPath)...")
let start = Date()

let semaphore = DispatchSemaphore(value: 0)
exportSession.exportAsynchronously {
    switch exportSession.status {
    case .completed:
        let elapsed = Date().timeIntervalSince(start)
        print("Export COMPLETED successfully in \(String(format: "%.2f", elapsed)) seconds.")
    case .failed:
        print("Export FAILED: \(exportSession.error?.localizedDescription ?? "unknown error")")
        if let err = exportSession.error as NSError? {
            print("Error details: \(err.userInfo)")
        }
    case .cancelled:
        print("Export CANCELLED.")
    default:
        print("Export status: \(exportSession.status.rawValue)")
    }
    semaphore.signal()
}

semaphore.wait()
