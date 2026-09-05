"""Append a verification-only module after checking the exact target blob."""
from hashlib import sha1
from pathlib import Path
import sys

target, harness = map(Path, sys.argv[1:])
data = target.read_bytes()
blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
if blob != "e555fce440872898e47fd5114f32eb15401d07df":
    raise SystemExit(f"Unexpected target Git blob: {blob}")
draft = harness.read_text()
control = """
#[kani::proof]
#[kani::unwind(6)]
fn negative_control_preservation() {
    // Deliberately false oracle control; this must fail verification.
    kani::assert(preserves_count(&[1, 2, 3, 4], &[0, 0, 0, 0], 1), "INTENTIONAL_MULTISET_LOSS_CONTROL");
}

#[kani::proof]
fn negative_control_uninitialized_read() {
    // A verifier-only detector control, separate from the sorting target.
    let slot = crate::mem::MaybeUninit::<u8>::uninit();
    let value = unsafe { slot.assume_init() };
    // Keep the read observable without introducing another false assertion.
    kani::cover!(value == 0, "UNINIT_CONTROL_READ");
}
"""
addition = '\n#[cfg(kani)]\n#[unstable(feature = "kani", issue = "none")]\nmod verify_income_candidate {\n' + draft + control + '\n}\n'
target.write_bytes(data + addition.encode())
if not target.read_bytes().startswith(data):
    raise SystemExit("Target implementation prefix changed")
print(f"Verified source blob {blob}; appended only the candidate proof module.")
