import Lake

open Lake DSL

package «selix_lean» where
  leanVersion := "leanprover/lean4:v4.29.1"

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git"
