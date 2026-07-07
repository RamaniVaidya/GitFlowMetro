# GitFlow Metro - Version 1: Basic Metro Visualization

**Date:** July 7, 2026

## Overview

This version represents the first working milestone of GitFlow Metro. The complete pipeline from Git repository parsing to Blender visualization has been successfully implemented.

## Features Completed

### Git Parser

* Parses local Git repositories using `git log`.
* Extracts commit hash, parent hashes, author, date, and commit message.
* Stores commits in chronological order.

### Graph Builder

* Builds a directed acyclic graph (DAG) of commits.
* Creates parent-child relationships.
* Detects merge commits.

### Blender Add-on

* Custom GitFlow Metro panel.
* Import Repository operator.
* Successfully integrates parser and graph builder with Blender.

### Visualization

* Creates one sphere for every commit.
* Draws parent-child connections using Blender curves.
* Separates branches into different lanes.
* Enlarges merge commits to represent interchange stations.
* Connects curves to the surface of commit spheres for improved appearance.

## Current Layout

* X-axis: chronological commit order
* Y-axis: branch lanes
* Z-axis: reserved for future expansion

## Current Limitations

* Branch lane assignment is simplistic.
* No dynamic lane allocation.
* No branch colors.
* No commit information panel.
* No repository path selector.
* Z-axis is not yet used.

## Next Milestone

Implement a dynamic branch lane allocation algorithm that:

* assigns persistent lanes to branches,
* supports multiple simultaneous feature branches,
* avoids overlapping branches,
* prepares the layout for optional Z-axis expansion.

## Status

Version 1 establishes the complete end-to-end workflow:

Repository → Parser → Graph → Blender Visualization

This serves as the baseline for future layout improvements and user interaction features.