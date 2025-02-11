# In-Class Assessment - Ray Tracing with Reflection and Refraction

## Task Overview
This in-class assessment extends our **Ray Tracer** by rendering a scene that includes:
- The **Stanford Bunny**
- A **Sphere**
- A **Cylinder** positioned in the middle

### Key Features:
- **Reflection:** The sphere and cylinder reflect the bunny and each other.
- **Refraction:**
  - Half of the **sphere** is refracted through the **cylinder**.
  - Half of the **bunny** is refracted through the **cylinder**.
- **Lighting and Shadows:** Maintains realistic lighting, shadows, and interactions between objects.

This assessment focuses on **ray tracing complex interactions between reflective and refractive objects**, enhancing realism in the scene.

---

## Output
Below is the rendered image showcasing the scene:

![Rendered Output - Reflections and Refractions](inclass_assessment_output.png)

The rendering demonstrates realistic **light bending (refraction)** and **mirror-like reflections** across different materials.

---

## Running the Code
Ensure Python is installed and navigate to the `inclass_assessment` directory. Then, run:

```bash
python3 main.py
```

This will generate the output image as `inclass_assessment.png` in the same directory.

---

### Additional Notes
- **Snell’s Law** is used to compute refraction angles for objects.
- The **reflective properties** use ray bouncing to simulate mirror-like surfaces.
