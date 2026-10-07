# Android independent-review corrections

Parent commit: `d86ee81a5622e026fc1cdf8875c2de67b8ce54e4`. No runtime or package changes.

The initial 13 checks missed a real missing Chinese font because the font unit test used a Resources stub, and missed an Editor/internal boundary because only the runtime assembly was compiled. The old Evidence, attempts, manifest and verifier remain byte-for-byte historical records. Use this directory's verifier for current source, not the old verifier's current-source assertion.

Corrections import exactly four full-font/license files plus the narrow GroundLootValidation reflection fix from iOS `d8f091cccca54649aa8fe733aa53b1743536aeec`. `provenance.json` records exact Git blob and SHA256 identities. The font retains embedded Adobe copyright and SIL OFL; no font modification or system fallback. A test authoring preflight incorrectly expected Google in the copyright field; inspecting the original binary showed Adobe. The test was corrected to the actual retained metadata before the frozen suite; no production font bytes changed.

Run `python3 Tools/validate-android-source.py /path/to/dotnet` for all 15 checks. This includes actual Resources path/file/import meta/license/GUID/cmap checks, all runtime source compiled into one DLL and the full GroundLootValidation in a separate DLL referencing it, and a negative control reverting only the two accesses that must fail CS1061/CS0122. UnityEditor timing/session calls use explicit small stubs. UnityEngine references are pinned 2021.3.33, not the required Unity 6000.6.3f1 Editor. These are managed/source checks, not Unity import, IL2CPP, Gradle, APK installation, or device rendering validation.

After a frozen run, `python3 Docs/Validation/AndroidSource/ReviewFix/verify-evidence.py` checks archived and current input hashes and the explicit baseline delta. All 606 shared runtime files remain identical to Windows PR #51 main. No download package produced.
