name: add-tool
description: Create new tool module in devpack/tools/

1. Ask:
   - Tool name (e.g: kubectl)
   - Method: [binary|pip]
   - If binary: download URL (use {{version}}, {{os}}, {{arch}})

2. Create devpack/tools/<name>.py with minimal template
3. Add to configs/tools.yaml:
   <name>:
     version: latest
     install_method: binary|pip
4. Run pytest devpack/tools/test_<name>.py -q
5. Commit: `feat: add <name> tool`

Use template_tool.py as base.