# Interactive assembly replay viewer

This is a static Three.js replay viewer adapted from the viewer used by the MRMG project page.
It does not run MuJoCo or the planner in the browser. Each scenario is an offline-exported bundle:

- `data.json`: timing, action annotations, camera, and buffer offsets;
- `scene.bin`: indexed visible meshes in local coordinates;
- `poses.bin`: downsampled world poses for moving geometry instances.

Serve the repository over HTTP; browser security prevents the `file://` page from fetching its
binary assets:

```bash
python3 -m http.server 8000
# http://localhost:8000/project_page/viewer/index.html?data=fabrica_car_current
```

Regenerate a selected bundle from its NPZ with, for example:

```bash
python3 export_web_replay.py \
  experiments/project-page-replays-current/chair-closurefix-render.npz \
  --out project_page/viewer/chair_current \
  --label "Chair · 4 UR arms" --fps 20
```

The four current sources and their physics-versus-rendering status are indexed in
[`project_page/README.md`](../README.md). Add future bundles to `scenes.json`. Assets load only after the visitor clicks `Load assets`, and
only the selected scenario is downloaded.
