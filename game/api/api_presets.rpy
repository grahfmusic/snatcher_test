# Common Preset Discovery API (YAML)
# Provides Ren'Py-safe discovery of YAML preset files for shaders and lights.
# Uses renpy.list_files instead of direct OS access to ensure compatibility.

init -5 python:
    import re

    def _presets_normalise_path(p):
        """Normalise game-relative path (strip leading 'game/' if present)."""
        if p.startswith("game/"):
            return p[5:]
        return p

    def presets_scan_shader():
        """Discover shader presets by category from yaml/shaders/preset and yaml/shaders/custom.
        Returns a dict: { category: [ {name, filename, full_path, effect_type, source} ] }
        Categories: crt, grain, grade. Legacy 'light' is intentionally excluded.
        """
        roots = [
            "yaml/shaders/preset/",
            "yaml/shaders/custom/",
        ]
        # Prefix mapping
        patterns = {
            "crt": r"^yaml/shaders/(?:preset|custom)/crt_.*\.(ya?ml)$",
            "grain": r"^yaml/shaders/(?:preset|custom)/grain_.*\.(ya?ml)$",
            "grade": r"^yaml/shaders/(?:preset|custom)/grade_.*\.(ya?ml)$",
        }
        found = {"crt": [], "grain": [], "grade": [], "all": []}
        files = renpy.list_files()
        for f in files:
            # Only consider shader roots
            if not any(f.startswith(root) for root in roots):
                continue
            for effect_type, rx in patterns.items():
                if re.match(rx, f):
                    filename = f.split("/")[-1]
                    # name after prefix_ and sans extension
                    name_wo_ext = re.sub(r"\.(ya?ml)$", "", filename)
                    preset_name = name_wo_ext[len(effect_type) + 1:]
                    source = "custom" if "/custom/" in f else "shipped"
                    info = {
                        "name": preset_name,
                        "filename": filename,
                        "full_path": _presets_normalise_path(f),
                        "effect_type": effect_type,
                        "source": source,
                    }
                    found[effect_type].append(info)
                    found["all"].append(info)
                    break
        # Sort by source then name
        for k in found:
            found[k].sort(key=lambda x: (x.get("source", ""), x.get("name", "")))
        return found

    def presets_scan_lights():
        """Discover lighting presets from yaml/lights/preset and yaml/lights/custom.
        Returns a list of {name, filename, full_path, source} entries.
        """
        roots = [
            "yaml/lights/preset/",
            "yaml/lights/custom/",
        ]
        files = renpy.list_files()
        results = []
        for f in files:
            if not any(f.startswith(root) for root in roots):
                continue
            if not (f.endswith('.yaml') or f.endswith('.yml')):
                continue
            filename = f.split('/')[-1]
            name = re.sub(r"\.(ya?ml)$", "", filename)
            source = "custom" if "/custom/" in f else "shipped"
            results.append({
                "name": name,
                "filename": filename,
                "full_path": _presets_normalise_path(f),
                "source": source,
            })
        results.sort(key=lambda x: (x.get("source", ""), x.get("name", "")))
        return results

    def presets_notify_applied(kind, name, category=None):
        """Show a user-facing notification when a preset is applied."""
        try:
            if kind == "shader":
                msg = "Applied {} Preset: {}".format(category.title() if category else "Shader", name)
                show_shader_notification(msg)
            elif kind == "light":
                renpy.notify("Applied Lighting Preset: {}".format(name))
        except Exception:
            # Silent fail if notification systems unavailable
            pass
