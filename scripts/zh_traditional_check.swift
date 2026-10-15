// Reads a JSON array of strings from stdin, applies ICU Traditional->Simplified
// transform to each, prints "original\tsimplified" per line to stdout.
// If original == simplified, the term contains no Traditional-only forms.
// Used by validate_vocab.py to detect Traditional Chinese contamination in
// the `zh` (Simplified Chinese) vocab field.
import Foundation

let inputData = FileHandle.standardInput.readDataToEndOfFile()
guard let terms = try? JSONSerialization.jsonObject(with: inputData) as? [String] else {
    fputs("invalid JSON on stdin; expected a JSON array of strings\n", stderr)
    exit(2)
}
let transform = StringTransform(rawValue: "Traditional-Simplified")
for term in terms {
    let simplified = term.applyingTransform(transform, reverse: false) ?? term
    print(term + "\t" + simplified)
}
