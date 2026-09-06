# Edit workflow

Commands run from the installed PPTX Skill directory, or use absolute script paths. Read only the applicable mode; preserve its data and rendering checks.

## Editing an existing PowerPoint presentation

When edit slides in an existing PowerPoint presentation, you need to work with the raw Office Open XML (OOXML) format. This involves unpacking the .pptx file, editing the XML content, and repacking it.

### Workflow
1. Read common schema/relationship rules in [ooxml.md](../ooxml.md), then the sections for the elements being changed. Inspect related masters, layouts and media as required.
2. Unpack the presentation: `python ooxml/scripts/unpack.py <office_file> <output_dir>`
3. Edit the XML files (primarily `ppt/slides/slide{N}.xml` and related files)
4. **CRITICAL**: Validate after each coherent edit batch and before packing; fix errors and revalidate affected content: `python ooxml/scripts/validate.py <dir> --original <file>`
5. Pack the final presentation: `python ooxml/scripts/pack.py <input_directory> <office_file>`
