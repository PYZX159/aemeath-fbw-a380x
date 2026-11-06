from pathlib import Path
root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
ONLY=['FUSE_1']
exec(compile((root/'compose_final_gimp.py').read_text(encoding='utf-8'),str(root/'compose_final_gimp.py'),'exec'))
