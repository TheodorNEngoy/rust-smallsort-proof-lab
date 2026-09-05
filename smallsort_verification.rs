// Local feasibility draft; not compiled with Kani or verified by it.
// Intended as a child module of the pinned upstream smallsort module.
// This covers only sort4_stable for i32 with ordinary integer ordering.
// It is not a complete Challenge 8 solution or a submission-ready patch.

#[cfg(kani)]
use crate::kani;

fn count_value(values: &[i32], witness: i32) -> usize {
    let mut count = 0;
    let mut i = 0;
    while i < values.len() {
        if values[i] == witness {
            count += 1;
        }
        i += 1;
    }
    count
}

fn preserves_count(before: &[i32], after: &[i32], witness: i32) -> bool {
    before.len() == after.len()
        && count_value(before, witness) == count_value(after, witness)
}

fn is_sorted(values: &[i32]) -> bool {
    let mut i = 1;
    while i < values.len() {
        if values[i - 1] > values[i] {
            return false;
        }
        i += 1;
    }
    true
}

#[cfg(kani)]
#[kani::proof]
#[kani::unwind(6)]
fn sort4_preserves_values_and_sorts_i32() {
    use crate::mem::MaybeUninit;

    let before: [i32; 4] = kani::any();
    let witness: i32 = kani::any();
    let mut destination = [MaybeUninit::<i32>::uninit(); 4];
    // SAFETY: source is initialized and readable for four i32s; destination
    // is aligned, writable for four i32s, and belongs to a distinct array.
    unsafe {
        super::sort4_stable(
            before.as_ptr(),
            destination.as_mut_ptr().cast::<i32>(),
            &mut |a, b| *a < *b,
        );
    }
    // These reads must be justified by the verifier's initialization checks.
    // There is deliberately no assumption that the output was initialized.
    let after = unsafe {
        [
            destination[0].assume_init(),
            destination[1].assume_init(),
            destination[2].assume_init(),
            destination[3].assume_init(),
        ]
    };
    assert!(is_sorted(&after));
    // witness is unconstrained and does not influence sorting. Proving this
    // assertion for every witness establishes preservation of each i32's
    // multiplicity. Ordinary unit tests below do not provide that proof.
    assert!(preserves_count(&before, &after, witness));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sortedness_alone_does_not_preserve_input() {
        let before = [1, 2, 3, 4];
        let overwritten = [0, 0, 0, 0];
        assert!(is_sorted(&overwritten));
        assert!(!preserves_count(&before, &overwritten, 1));
    }

    #[test]
    fn duplicate_multiplicity_is_required() {
        let before = [1, 1, 2, 3];
        let changed = [1, 2, 2, 3];
        assert!(is_sorted(&changed));
        assert!(!preserves_count(&before, &changed, 1));
        assert!(!preserves_count(&before, &changed, 2));
    }

    #[test]
    fn order_and_permutation_are_independent() {
        let before = [i32::MAX, -1, i32::MIN, -1];
        let after = [i32::MIN, -1, -1, i32::MAX];
        for witness in before {
            assert!(preserves_count(&before, &after, witness));
        }
        assert!(is_sorted(&after));
        assert!(!is_sorted(&before));
    }

    #[test]
    fn length_mismatch_is_rejected_even_for_absent_witness() {
        assert!(!preserves_count(&[1], &[1, 1], 999));
        assert!(preserves_count(&[], &[], 999));
        assert!(is_sorted(&[]));
    }

    fn ternary_array(mut value: usize) -> [i32; 4] {
        let mut result = [0; 4];
        for item in &mut result {
            *item = (value % 3) as i32 - 1;
            value /= 3;
        }
        result
    }

    #[test]
    fn finite_oracle_crosscheck_matches_sorted_multisets() {
        // Exhaustive oracle test on this finite domain only: 81 * 81 pairs.
        // This neither executes SmallSort nor substitutes for a Kani proof.
        for x in 0..81 {
            for y in 0..81 {
                let before = ternary_array(x);
                let after = ternary_array(y);
                let observed = [-1, 0, 1]
                    .iter()
                    .all(|w| preserves_count(&before, &after, *w));
                let mut sorted_before = before;
                let mut sorted_after = after;
                sorted_before.sort();
                sorted_after.sort();
                assert_eq!(observed, sorted_before == sorted_after);
            }
        }
    }
}
