from pathlib import Path
import json
root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
exec((root/'helper_export.py').read_text(encoding='utf-8'))
assets=root/'artwork/assets';sources=root/'artwork/source';sources.mkdir(parents=True,exist_ok=True)
im=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(assets/'aemeath_pose_B_official.png')));im.undo_disable()
layer=im.get_layers()[0];layer.set_name('Official Aemeath + mech pixels | silhouette panel')
backup=Gimp.Layer.new_from_drawable(layer,im);im.insert_layer(backup,None,1);backup.set_visible(False);backup.set_name('Official full composition reference (hidden)')
core=[(434,247),(478,255),(535,256),(575,246),(590,242),(620,269),(647,286),(667,283),(685,276),(673,301),(663,326),(676,347),(661,369),(649,382),(655,398),(679,414),(692,407),(714,407),(735,416),(752,432),(772,439),(802,419),(820,398),(849,382),(880,372),(904,367),(913,364),(905,380),(886,390),(878,405),(890,404),(911,386),(936,377),(963,374),(981,380),(986,394),(979,407),(956,419),(948,437),(974,421),(993,417),(1008,425),(1004,442),(982,459),(966,478),(958,493),(939,509),(911,521),(875,524),(840,517),(819,509),(815,529),(850,543),(873,556),(891,574),(926,591),(883,591),(871,612),(866,641),(870,664),(888,691),(916,715),(886,715),(865,702),(847,686),(862,716),(888,741),(907,733),(918,718),(915,750),(898,785),(886,815),(875,847),(857,880),(838,914),(819,949),(802,974),(787,996),(769,1022),(744,1048),(716,1060),(690,1060),(663,1048),(638,1042),(610,1029),(582,1014),(560,990),(544,965),(526,943),(510,915),(490,885),(473,857),(455,830),(442,799),(430,779),(448,758),(472,746),(490,733),(514,720),(531,705),(538,689),(523,686),(509,696),(495,699),(491,687),(500,665),(505,647),(481,648),(451,655),(419,670),(398,686),(374,708),(364,716),(363,702),(374,679),(390,660),(405,645),(421,631),(399,632),(377,630),(355,616),(337,606),(318,602),(304,589),(292,578),(289,563),(302,568),(314,574),(323,571),(329,556),(328,537),(338,541),(347,559),(351,572),(359,565),(370,548),(385,535),(397,522),(407,508),(419,488),(431,465),(438,446),(434,431),(443,413),(448,398),(439,380),(445,360),(460,354),(475,373),(481,390),(507,390),(520,365),(533,334),(544,309),(554,286),(546,274),(520,268),(495,266),(466,260)]
left_fins=[(423,385),(393,384),(358,392),(327,398),(301,399),(330,407),(368,410),(403,403),(427,397),(430,402),(418,424),(396,446),(373,461),(346,472),(313,481),(280,484),(310,488),(348,486),(386,471),(419,449),(444,421),(458,398)]
top_fins=[(430,197),(464,218),(497,235),(533,246),(574,248),(557,260),(521,250),(491,236),(458,216),(433,210),(429,198)]
arch1=[(640,361),(681,354),(711,338),(735,310),(758,278),(784,250),(813,226),(844,207),(865,201),(886,201),(896,207),(870,210),(844,224),(815,245),(789,271),(767,306),(744,337),(717,360),(686,377),(647,383)]
arch2=[(668,360),(707,338),(741,306),(772,280),(803,258),(838,242),(874,233),(907,234),(940,241),(978,240),(1012,246),(1038,260),(1056,278),(1069,302),(1069,320),(1056,333),(1041,340),(1053,320),(1055,300),(1044,283),(1026,268),(1007,258),(979,250),(947,252),(909,245),(878,246),(843,259),(814,280),(786,306),(760,334),(733,358),(705,376),(679,382)]
def polygon(points,op):im.select_polygon(op,[float(v) for p in points for v in p])
polygon(core,Gimp.ChannelOps.REPLACE)
for shape in [left_fins,top_fins,arch1,arch2]:polygon(shape,Gimp.ChannelOps.ADD)
Gimp.Selection.feather(im,5.0)
mask=layer.create_mask(Gimp.AddMaskType.SELECTION);layer.add_mask(mask);Gimp.Selection.none(im)
pdb_run('gimp-xcf-save',image=im,file=Gio.File.new_for_path(str(sources/'aemeath_starboard_cutout.xcf')))
im.remove_layer(backup)
flat=Gimp.Image.new(1300,1080,Gimp.ImageBaseType.RGB);composite=Gimp.Layer.new_from_visible(im,flat,'Official pixels with silhouette mask');flat.insert_layer(composite,None,0)
save_png(flat,assets/'aemeath_starboard_cutout.png')
metadata={'filename':'aemeath_starboard_cutout.png','eyes_px':[693,450],'width_m':24.0,'world_y':13.0,'world_z':3.15,'mirror':True,'canvas_px':[1300,1080],'crop_offset_px':[0,0],'method':'GIMP original-pixel silhouette panel layer mask with 5px feather; no redraw, no upscale; main mech/girl kept; outer poster starfield removed'}
(assets/'starboard-character.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
samples={f'{x},{y}':list(composite.get_pixel(x,y).get_rgba()) for x,y in [(693,450),(625,330),(690,550),(50,500),(1170,550),(650,60)]}
(assets/'starboard-cutout-alpha-check.json').write_text(json.dumps(samples,indent=2),encoding='utf8')
bg=Gimp.Layer.new(flat,'Preview matte only',1300,1080,Gimp.ImageType.RGBA_IMAGE,100,Gimp.LayerMode.NORMAL);flat.insert_layer(bg,None,1)
Gimp.context_set_background(Gegl.Color.new('#eceaf0'));bg.fill(Gimp.FillType.BACKGROUND)
pre=Gimp.Image.new(1300,1080,Gimp.ImageBaseType.RGB);pre_layer=Gimp.Layer.new_from_visible(flat,pre,'Preview');pre.insert_layer(pre_layer,None,0);save_png(pre,assets/'aemeath_starboard_cutout_preview.png')
pre.delete();flat.delete();im.delete()
