# Installation

## Prerequisites

Before using GitFlow Metro, ensure the following software is installed:

* Blender 5.1 or later
* Git (available from your system PATH)
* Python (included with Blender)

---

# Installing the Add-on

1. Download or clone this repository.

2. Locate the `gitflow_metro` folder inside the project.

3. Copy the `gitflow_metro` folder to Blender's add-ons directory.

### Windows

```
C:\Users\<YourUserName>\AppData\Roaming\Blender Foundation\Blender\5.1\scripts\addons\
```

After copying, the folder structure should look like:

```
addons/
└── gitflow_metro/
    ├── __init__.py
    ├── panel.py
    ├── operators.py
    ├── parser.py
    ├── graph.py
    ├── visualization.py
```

---

# Enabling the Add-on

1. Open **Blender**.
2. Go to **Edit → Preferences → Add-ons**.
3. Search for **GitFlow Metro**.
4. Enable the checkbox next to the add-on.

The add-on will appear in the **3D Viewport** under the **GitFlow** tab in the right-hand sidebar.

---

# Using GitFlow Metro

1. Open Blender.
2. Open the **GitFlow** panel in the 3D Viewport sidebar.
3. Click **Import Repository**.
4. The add-on will:

   * Parse the selected Git repository.
   * Build the commit graph.
   * Generate a metro-style visualization of the repository.

---

# Development Workflow

If you are modifying the add-on during development:

1. Edit the source files in the `gitflow_metro` folder.
2. Save your changes.
3. In Blender, disable and re-enable the add-on (or restart Blender if required).
4. Test the updated functionality.

Keeping a separate development copy of the project under Git version control is recommended, and only copying the updated `gitflow_metro` folder into Blender's add-ons directory when testing.
