"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/963c5f8b81c045fcab90387bf3aa5143/part_002.stl', 'relative_path': '963c5f8b81c045fcab90387bf3aa5143/part_002.stl', 'source_sha256': '3a7de7c6ac7f5c28d0bf4db538bf5a234972b055d070caf9b34214e77ae1866e', 'input_faces': 466, 'input_vertices': 289, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17240826785564423, 0.08140899240970612, -0.19495655596256256], [0.17240069806575775, 0.4164932072162628, 0.12697455286979675]]}
GEOMETRY_BASE85 = 'c$}r133OCN+J<ieVF`;YAz`;iWe=ciCTzK^BHJJ;$RLwOc2r;pvdc6eh>&pxA_D@!MjcRa31C8E4Cz1<KyZ{T$RY+@#s!68CI~vCe^=FW@6;{wpYxx8a?W?&C$Gg<U)8OyuGBpa8&siUoTYw#WsN;?{;l<mEK5XnE6$odVdktU<0hoFn>J%!lvPXm;>Xd9p$`ukHY&=RZ7paqenQ%~nJv2dT6CY7)FRQ>V&e3fvu2K+mO6dr_zA-AKlX{V2@yYS^4J*@BEPrnkd&P0>)0yM_q6Z-`4bx{!9TBdabZLQqx&39iD)S1VpgH%`=)J{zSU;kPTjW;cRV5eq;9KH^gP4ID!=B+Wl~2@4+}qde8X}1`@dsX>%Ns2t=hM1AlrwgO_RP|a_orsJ@9VTHw!i2dS#2MbM{@b&d{;U{nCHUQgzN6`iAZYb~pV%`1S+iJnaK%OH@7av42d_e0yGPRZs5l`9gzZ?#q|;|KYZ<9OtlCLxq}e2d7Hk8uyFG_eT#sE$bin(QZ$kRSTqVH)|;U(lNdBWL-UyWu8EdoPt8l55!hIAoFi~xKQ^?n@%c`?XRSH^4KvSO5YlBa;F?uS<hVg9Jgo7{H2`=-YeAnQ1%I#-#7T?UfmB|YoYS@n6pdIW8cV;zTLcAmh^wj-Ywf--hWum&)wH${ekO4cF6HIulKR6=iKF-6wNPvySMUlx=7z|b$?m<_s>5o^X|4oy6-!&P5Ob}M+#;C?UuYG^H;y~U72UqCkF~OKakf^`hlfYigmv<s<ZTiU3Pog2j`5JzHeHhr+o;&bldZu_SV`rrSJb;KX3jX(fKm}okP5SyGNw&`=GDKw+C;LzFnuS$M@~~D8Ib=1F^^R%d6j-elcI42Vc?Ko8>xevn#JWKd|zB<qvOKtox<Mk4WF1oat%rd#$b<Z|KxRp7w#OaniRxpXhCWW3g&qWqxtF{=>aJ?X8|_-a?Bzd;R4Vr0-8!?(O%;QZ*0b=auURcJ}hl!-=bEo^5ZP0sK;9T%oJU@0B+{zT|Gw_Z#yQSpT5(eeEwO|N27d+mjzVCG$*eQlR_RrQY&$6k57bea<I#QvPj)YF`?@VwcAsm?`(Az|p2}$>;R*qD+~;|7F?UuHSsO?gwieQ0>c>y)FA)I79l@;Dz$}mab$y;QNohD1G1JH6A~RU;0AJV%@i&`d+P*>66O!gIgc;<gr>mq1MUpR^EPRKB?Bjq&1#AAwEaGH4Q!OZPtUY<rYu-zys^mIx+HF8(vh;*U0a$6fd7w$fz?kG(q}-x|6-_e|TIy_huR1`N8)kxAL^N<~}EVoAu!DF?5ss?@s-OZ>{Sf_qEWTvV$H!x1QVwgUvRFb>BZ_zVxjPah~?21D6)b`g5xl>waK)uJrAZKkf6>^J3k7YJHB_ulsg`=KE#)Zzg;CwL8@<mia$iP$b9yQ~yontt-bj*OlX&>&o%Xb!Ga_x^nw9)|K0@v9287Sy#?}X!_22bNe;co8z17&8^2+Z*D!tdUN|V)|=bjSa0sU8SBmM*H~|M;&bce^Gz&~`%mbpZhLjVbo@$nPRN+5&L#WXX2^b5)>PlKQ;zRV(fuw9m7mwBK=xlyOZs-w>38IKPwrIfAK#B}KNovI_pN6Z$?tn#mhX`6`|z!|HtyGbyX&Lsduqf#J?(?|c9lc>Jb8@Im*a<yZCCSV<gtz`-^^pLSfS1tMxB0qpHXKpOPyDIZPUV@e*5G}Ka|zxpza6Gw^X0Us8yakR`)ZW&##+jQjz?ehSKj;&v$3Z8d*>Bn<u5;>{_Ajm)5$Wp6{XJ9GSP}4%NP8HT8XQd1SWk2QCbgd8}4TUX#C%7%hE!cs=<&Vt=)Gm+l9nHc3C!dXhX>Tf=&)e$RJT-(LlvWqbVDvt<6jj@a$8j>AKrm-+himFv@&-Yewshcs5_=c{+9b8WMn<x+2KlleoxzV{v7500*?@-G`F|6Z`Zj{Bl#IrHrJ!SvzM5A7)`(*4l9%hC_N-@@bjN8KUkKk&@zeY$Tii&gt%Nk5P8FHrlZ|I&&Bo_Z$bC_m|D*wgQfxd)}+{$6jtD~gZFexI0{<MB`5RQ`!89^V?UNX<{J3-5UHSL>+er(*mYp7v#vl)rIl$W!N{waRZfW~=V|=2Tbv$z3}=?S0#N$meBE&&u}n+u$Mf91Hv8dgebVU9}%kB{xOycg|VW{()Y3y6^AVNd3K#ax`1_BY*cOKX=O>-S^eJc}C`$yHM_9R^qPZDdnsm$2ZrH@1udwr<AikUEf%r{s+6SNhxRjmyQ}Gee-kV_~z%x-}-gwo1at1zvXjUc22c7_5sH?_W^%&e1^<x?AwlS?%R%U?%R%U?%QsDW8ZdsbKiFREwj}5|I729e$9Q`t;g86-F}UI+s$w6+ipF^zU}sF?AwlS?k8?N#=h<5G4^fiU>jAB`90hI+4Zsx<NMn2&F|~dl);<i@5Z^y@y&CW<D2I$$2ZSirth4)+<uL7m)oy#?s9zd+-3UCxy$X>ICnX|dG2!SG0t6XJ;u4q?bkSWx$TW}mpgC9xy$X>ICr_eac*~f^L*}(%Q&AqzIi@(=f^moyS{Ng5Bz>wW_jzx@y&JO_~trsd~=<czOzo;evNhF_G_#Y$2Zr5o8MRuj&H69w_jsDxcwUI!R^;r4{m#7J-G8@tOvJWb3IJyuvz-X-}RyG$;vnWuJ?CcB7O7T!12v{1Ak1m^v!!7$2aeJ9N)a>aeVWh$IWBh^SJGed!Ac-?s**FyytO!<DSRu*SO~~ednIXod@Hd$8B%i^EkeF&*Ro_-1E43jC-Cy+Osdo`iy%>$2adG9pAi%bn_VZkdANOLpr{B4{7?=ce6e1ozIv5+LIpNytj0H<KEKrO9y!KTNQ)(<<)84b2`3x&*{#aanI@IH|{z8MTb1&a(wHRo-fNfjQeE!#^4<?uW>IOT#zmA(an48P=8yVPj9(D$G_$N9RHU4bA0puJa9psbItpI$2af)9pAkFcYO2y-+!UMnn&aPh2xv=FC5=|f8kq`DZg*b_biTYzGv~x->iJ&J&WU;?^%59r^!0Z_dbqqzW1>crc2*^ujKgVd!^Fk+Uk4Jc+chdp7&Y9Ja6@0?RWRtN8&9@L{%%!nmAT_r6)}B<7oM>^rm$BKfTiH)TPUR`%3Ruks5A~L|Z~|8?*`B25yBmg<HX`Q6JnIPDJm36XAB~op3w&9`r8w9=HSA4DJATMw`Q(;Vx)PxC@+wwt$7+3n#%t3BiNWPViuOAleZg2oFH-h6lj?(e`kExG&lk?hE%p+rWKb8*K&Ka0=QQPJw%&iEuBtH`)&F4fjLuf&0Ptp&j7+;QP_e@cr;0v<o~49)c#pNzC;SLhvL)@MLr_JQ<#d4umJd<Iw@|c=$22Kl~W%NBhElcnsPH9s@s$+VG?BC^Q8g1wVrJf**l@gZ74h1CK`g!K2~dqW8hSg~y`z!(-ub=pc9;JOLd74`Hq+5UE=GR4r$!)^Dm-TdG!nsy4<{Z5~p!xk}aMGgX`ORPDK>YR@iJd%l95HIPc(snjjFVw7c7i9{43*dhe~+fpI;CrgFko0bZ}H!Kx`f3#Ex{+Fdf@XwYC!M|841V<BsD-eP!5rQidf@9E%a18uUONHRSqfxL3!B<fW79sdMRE+aGLh!ffPw=<!*XT|7Yxpbl2K*KL4f-Se4SX5>7knB19{m~q9=?M90$+izp<*7d@w?!EpcP;dg0G{MU=f0UKr6!{1ec*Pa18TZMhGq?1Ybb^4qt%JqgUbc@LBXb_$+)H{T4nAm!Mz6CGbh~EBGXQ3jGE?1%HfQhChbSpx?u1;B)8|_#FHRdJX;r{uKQO{3(19y$)Z5KSO_jKZ7r!WpEjDeTfkKJ|XxJdI3HJ7o+FlVt7A#7Tyns(9>`TE<{V<Lbw1u2^YY7(NpkVxCs3iE`s-=XW)JC0rVVv06vI*0w07Aqo2Zu;Unlp_z3&~`WgHId=$L|Ut+G0qG9+b?EKrXmOrf35Z3ApYhwv(;|*(b64vG|tj%p$oBy!(jKbP;3~SF?@FDbl_@zj!wZxwrmi1mF@+0vwA^1f?@Nz=%R6_6+Lhv#|@H%u0yoG+&p=;rF@G|siEzi^B7MiT}l}!IayK41xrADEPw3-(&4x#I{ajj>pLSNU${yOs^^l$Kca6bAaoDXjyzGQqap|7G}!mq-ALH`E-1rDOG!$J53bUpk6yaHVWuYi}JUEwA0Vl)|E3_puL4L=KKplji^j4gvU8CsqUt*;ENo(!$#3~gK)+SoIgn+);`-W7>=BJnnw1;2^zK(pZO=o@Gj{1&<s&4PEMIcOG~MSnSHHk<?JMq+j(=0#!_ng;(4osOo#PomS%G<XI&6HSAkLg%1qa2oy1Aq3Aw7r=Aj`RGDe==1P=_&GxG9yAZmW2}47Z20p?d=ZJQ=r&mBpJAZ^SZH@xXg65s@8PZRYC`ZI2*LHxZg4%gD%u^c3Rgn|a5Xpq{WF{ZZ$h`ho8a4`lzst=5Zn;`92OzCKDreaA-D#*8eYxV1d9+{JxYb(RfOO;v>qG>S3#@7Rp3~(8XOD9qX}?4yaC+=Z(^()_+4;K#@-OF2{%CN!wujBv<6&*u_X|KYY~E1GJY}Um5e<OUJ2JitH8D3N@y%x39g97!xiB==mxkBypfPT;}_$sLkMnyHh`PJjnD)*fw46r1lJ}6r&~(J*wPteEjS&njaGtd!<EsBaAi0Ktpmrvb<vG*T{x4Few0!%&box)rf3tmDcl%s1UF)Ajrq5tosSTFJK7k&9gah5!*TFOmQpbng2mqRS4-_bf5qE_ro($+XHOF>_PM#}1BBp*&~!MR`F)5GTpg_pSBEV$#`@2X;Apfi91Yh*GvS(WgGe+&A4fCc$KlO{;CCZYHA-nLnhA>#9FK};5YMyl!NVf{uOl%$5{)DAL?jwUVq_%hN8(SBcm-WU2wsZThnK=VB5_+Jo{2;Sv?p8vjzW9DJ@~g#gy0&4;D^zX@Pp_GbR;~Innn<U|40Zvj-G%&M312-;CfL?tBLs;6crs;;eY#IP5$!}5QTgG#}o5kdatwfe_0aA<z8+N8x$ix$B~5+Ee{S;#Lb}fKY9d31p'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
