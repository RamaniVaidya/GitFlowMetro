# GitFlow Metro V2

GitFlow Metro V2 extends the original Git repository visualization add-on with a topology-aware layout algorithm, improved support for complex Git histories, repository analysis features, and an educational Merge vs Rebase simulation mode.

The main goal of V2 is to improve the accuracy of Git history visualization and transform GitFlow Metro from a repository visualization tool into an interactive learning tool for understanding Git branching, merging, and rebasing.

## Major Changes from V1

### 1. Topology-Aware Dynamic Lane Assignment

V1 used a simpler lane-assignment strategy that was sufficient for basic repositories but did not correctly handle more complex Git histories.

V2 introduces a topology-aware dynamic lane allocation algorithm.

The new algorithm:

- constructs parent-child relationships between commits;
- identifies branch points and merge commits;
- preserves the first-parent path as the main continuation path;
- dynamically allocates lanes when branches diverge;
- releases lanes when branches merge;
- reuses released lanes for later branches;
- supports positive and negative lane positions around the main lane;
- handles nested branches;
- handles overlapping branch lifetimes;
- avoids hardcoded branch-to-lane mappings.

This allows the visualization to adapt automatically to the structure of the imported Git repository.

### 2. Lane Lifetime Analysis

V2 introduces lane lifetime analysis to determine when visualization lanes are active.

Instead of calculating the maximum number of lanes from the number of unique lane identifiers, V2 analyzes the active lane intervals across the Git history.

This provides more accurate repository statistics and better support for repositories where lanes are reused after branches merge.

### 3. Support for More Complex Git Histories

The updated graph and layout algorithms have been tested with repositories containing:

- simple branches;
- multiple sequential feature branches;
- lane reuse;
- nested branches;
- overlapping branches;
- multiple merge commits;
- branches with different lifetimes.

The visualization automatically adjusts commit positions and metro lanes according to repository topology.

### 4. Local Branch Detection

V2 extracts local Git branch pointers directly from the selected repository.

The add-on can determine:

- available local branches;
- the commit referenced by each branch;
- branch-tip commits.

This branch information is stored in the internal repository model and is used by the Merge vs Rebase simulation system.

### 5. Improved Repository Statistics

V2 displays repository statistics directly in the Blender sidebar.

The statistics include:

- total number of commits;
- number of merge commits;
- number of branch points;
- maximum number of simultaneously active lanes.

The maximum active lane value is calculated using lane lifetime intervals rather than only counting unique lane identifiers.

### 6. Improved 3D Visualization

The visualization system has been improved to provide clearer Git history representations.

V2 includes:

- dynamically positioned commit stations;
- visually distinct merge commits;
- lane-based materials;
- straight connections for commits on the same lane;
- Bézier curves for branching and merging paths;
- connection points calculated from commit sphere surfaces;
- improved branch and merge routing;
- reusable camera framing;
- automatic repository lighting;
- commit information boards;
- transparent information-board materials;
- branch and merge topology information.

### 7. Commit Inspection

Users can select commit stations directly in the Blender viewport and display additional commit information.

The information board can display:

- commit ID;
- commit message;
- author;
- date;
- branch information;
- merge information;
- parent relationships;
- branch-point information.

Commit information boards can also be hidden without clearing the repository visualization.

### 8. Clear and Rebuild Visualization

V2 introduces a dedicated Clear Visualization operation.

Generated GitFlow Metro objects are tagged and can be safely removed before generating another repository visualization.

Reusable camera and lighting objects are preserved and repositioned when a new repository is imported.

### 9. Non-Destructive Repository Simulation

V2 introduces an independent repository simulation layer.

The imported repository model can be cloned before performing educational Git operation simulations.

All simulations operate entirely on in-memory repository models.

The selected Git repository is never modified.

No destructive Git merge, rebase, checkout, reset, or branch commands are executed.

### 10. Merge Simulation

Users can select a target branch and a feature branch and simulate a Git merge.

The merge simulation:

- clones the original repository model;
- preserves the existing commit history;
- creates a synthetic merge commit;
- assigns the target and feature branch tips as its two parents;
- updates the simulated target branch pointer;
- preserves the simulated feature branch pointer;
- rebuilds the graph and layout for visualization.

The simulation demonstrates that Git merge preserves the original branch histories and introduces a commit with multiple parents.

### 11. Rebase Simulation

V2 also provides an educational Git rebase simulation.

The rebase simulation:

- determines the merge base between the selected branches;
- identifies feature commits that must be replayed;
- removes the original feature commits from the simulated result;
- creates new synthetic commits representing replayed commits;
- assigns new commit identifiers;
- rewrites parent relationships;
- places the replayed commits after the target branch tip;
- moves the simulated feature branch pointer;
- preserves the target branch pointer;
- produces a linearized commit history.

The simulation demonstrates that rebasing rewrites commit history and creates new commit identities.

### 12. Original, Merge, and Rebase Views

V2 allows users to switch between multiple representations of the same imported repository.

The available views are:

- Original History;
- Merge Result;
- Rebase Result.

This allows students to directly compare the topology of the repository before and after different Git operations.

## Educational Purpose

GitFlow Metro V2 expands the project from a Git repository visualization tool into an interactive learning environment.

The Merge vs Rebase Learning Mode is designed to help students understand:

- how Git history forms a directed acyclic graph;
- how branches diverge;
- how branch pointers reference commits;
- how merge commits contain multiple parents;
- how merge preserves existing commit history;
- how rebase identifies commits after a merge base;
- how rebase replays commits onto another branch;
- why rebased commits receive new commit identifiers;
- how rebase rewrites history;
- why rebased history becomes linear.

Students can import a real repository, inspect its original structure, simulate a merge, restore the original view, simulate a rebase, and compare the resulting Git histories visually.

## Safety

All Merge and Rebase operations in V2 are educational simulations.

The simulations operate on independent copies of the parsed repository model.

GitFlow Metro V2 does not modify:

- the actual Git commit history;
- local branches;
- the working tree;
- the staging area;
- repository files.

The original repository remains unchanged.

## Current Status

The current V2 implementation includes:

- topology-aware dynamic lane assignment;
- lane allocation and release;
- lane reuse;
- lane lifetime analysis;
- nested branch support;
- overlapping branch support;
- local branch detection;
- branch-tip extraction;
- Git commit graph construction;
- graph depth calculation;
- dynamic 3D commit positioning;
- improved metro-style routing;
- commit inspection;
- repository statistics;
- reusable camera framing;
- automatic repository lighting;
- clear visualization functionality;
- independent repository cloning;
- non-destructive Merge simulation;
- non-destructive Rebase simulation;
- Original, Merge, and Rebase visualization modes.

The next development stage focuses on improving the educational presentation layer by visually distinguishing simulated commits, displaying original and rewritten commit relationships, and providing contextual explanations of the differences between Merge and Rebase.