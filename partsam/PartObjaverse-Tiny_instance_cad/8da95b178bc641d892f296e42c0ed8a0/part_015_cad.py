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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_015.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_015.stl', 'source_sha256': '9b4d69f30a6e1a6dceb1a23351a16f65a125cfa90f5e565396ad8f59e1d252c9', 'input_faces': 288, 'input_vertices': 175, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4492678642272949, 0.12149833142757416, -0.3097681999206543], [-0.028723537921905518, 0.47584807872772217, 0.3090236783027649]]}
GEOMETRY_BASE85 = 'c$}q~2~<_p8pk&(C~9g%DxgTEplOMsf=YPA)Igae6K4>aa=<_l740|?Lgs*y6M97yL~x4K)I3MRA;lrdDYeBjn^&5Z)q5tryT9*$xQFts_11fLt#AE*_s4hl+2?T1W&`2F8a8qk{CY-oUes{)H?4$_)m%7>w78U+NwIOMFHWB^$4;~&FJDIHhK>vgA8jYn#5}LbajCH>Uj010{Nw$+x_NlTC#TFziJ3kzIc0L3^h08%rp8%)YGTZcIP3e)J$!q2^YH1?&11gD|M+Su=Wt%XsaeD0i8OrxP3pJ4^1XWYee#wHhvVd%cPuu0-SBfOie##P?j$eL-(}zLi9?#nM;m^|&4V(P$Q&Mj>G|XJjyqrpkKa3}qTX@gYYcB3_lt!*PUoE!^^Obg(FGpIt?Pea{}H|Ka_+dfKl)epdSyA!t7JBLW$f?@^E^e~3?3)_1pDCHBD1eC{NYVJ&#Gkhk34C7VfpT$X7bUs@K-*dc?!=2?(bApZ=Qy?cvjV$r*djE`{(XeQvZS6Q<~X#gpZhait^e>9{=(X@?z*7z7Ft~EAY4TXnZ|!IQO?5bHY4+op*sZ#=p~_$LUi|UIZjjf1USbuUrqOeq~!L_TOgGd!dA#(@ehRJNO%Y&e8bg&H1`j6|x`SgZd3`ImcfAy)E^NtBv@6xO$Q27aUThnSAs$_%C}^(R^~x-=O}NQa`58r<b15%szm<>a^wz9cSf7<Sir4a{slaXEn2rWUr_E#QiRjJkI^^>3HfqKfa!Z|B1cc+Jom+^9uQzu0#2J4)XP{^WE6jUH`Q7&*<w8j-Swb=UM#yg%^$4>$}JCeLiy<dA*MxdGS2%H+bR8Ud8>U#&5Y!{liCAQ-A+7zMtVm2z>Hjx}WvNtJ(KnhJJod4X+qJ8P93*7uV?P$8LQ}J~V-zufO?2_Vj#-XD_io-1aiPZ^7$^;l&a7bY3@<qD|Z%k;Y#9&d+si7J22ufqGs&u;>bXU;esI_Do^Fy(3@8G`~`_R}KHwm0fgR`=*kwnT_>uq5DzI<W*yxJoLj6x^A;4kykc))?0s+S)+KI@PqZd9`-8FXXA(LZ+9&<`)I?DI79OhzeI3<<{uU2`54|}c+5wH1hEef<@KtgL#bx+HHKeV$m8E1!oE0%efYg2n#o7+gwHxg<Ewpq**AN@zFBppX7V1*+3VX6)B2=$=*086@iVV)6<4X>@X<Hf>*F>4`d6+zpZ79&y*jvy$A`C+vlo%M{JDvLUZ&&zx%VXbz_t8b8(!=quinZyOX>N5{fYp74)^3zf1O{+UJsr}{mOyw$w%+0;B~C!Sn99yd)cccfjoX}C3(w;NwkhA_FkW8CSMcDUcKbX&uilf?sv*!f7hA&;cK2^uODf`&%Mhr?$6#&Uc9jRqGs|nIqa2xt-45GAH0g^S?$Q{Pi*rGn#o%}Wv|!%e4am-&ErH(;r`LHso(G(W7sRdOt?Vf&mBNs^ev_1sT~~X`WRj{{NW#XUh#hH-}#*VkJI>i!iyE~*(3S-7gc>q-_P)UwEn2L-wdxrz#I3Qs3b4ee$DGuZO;>$$t&>6I#<5GzKQ1kyXqC{KRS%=f5R(=zwgS=S6~#+C*wo*jlbpR1zyaD_dmqXOGY~$=T^`)@_y?}w8!~E-xA6}PCU-d73_D1?b06SUGH*#brYV?f@=2SpS<o}d{j+&-R-*Bi~CK=seiGnM)M19U1|2}Qur?)@xEs4AMcS5ol0KJ^yi;b@Ol_~wI#2k>dAZD?{bX${ZH`v39q}tr>;55&-+dCqWv?xZmSD+XeRGr_`B_PQ2+7k?3X{!KFTeR{69{Tw``iq-tXg&G?Q2J*(=q1`MmOU^3i8jl2;vr_`Kl7S@wFNH?Q}0<vh-w4|sg#2Cu{L9(&=_OZdDV=CjuyvY)hy&kJ5L{Kf8kURO4dujy{j$1D6TPcwPp4X^g1^A(w2@2B(KRmtn-?5An}Q|C+BD^8DiAGEQU{q(o_zAq~KSTp-%_DbMd-XFQ0+(*8MKQBf!<#h(WrWk&}AG{9CTh9HL%6J`Xy_(k<_?l|?eRHT^{Vs7YU7sE~wC;$2YQA6LEj`&Q%}(+2-Sjo?Uv`?j{)RXA!&|c1dkpBv&wa_b-E_a*evQ^mWnmeutA<y<V6TR5<#qM*rsT!Z_3Y0zx}=%B4sY4;JNI{Sr{_}H-H7%%>Of~cUw9o}zwwaIulN!@_o6JA`^z=%hgS_BTEy4$^uK6-q<CMTeU9q%h}Ttk9bS~(p>@*w`vLpxHnjez{R?>i46o+EUtUK0R*`U(?nm+Mx~t^xe0f?kdDZX>&Yh<IuXDIR=??o>GwJ>@yb3SwP2>CG$Da!M{Ce{GGcJ?XVZ*EN>Vs+g^Ze!p_8|+|-*rE!nY;*v&vM|O^BFC+(fPJJ`5C=W^r_HHUTM!>w{zqDk=xz^@(<l_@NwVges~>TtjNdjuWlCldhWnm^nTX&bRYlC7aiWm_s`HR<Zo|dpXXknJ<iu2-CD2z*An*OZ|>I~=NE_Wr<@SCndYBh|2e%k*7MU*<W);c_Uqm+c&x9DETAk;$|pZ;rfr<?dVeKpmDOUhXkkTbISOYHA7lCx34K9`x_tbfNRoQ}SAQbu>F4+V{)wcebq+6B>uHqaF4pRb?2dc^+#T$L>;d)x_d)gs_W}1p_5}9=dm~>2dxN_np9gmXcSd@GJA*qSp9OaWyCXfo?%=jaS8!Xf6S6hf3G9e$1$G2CMz#Pq2HPW>gYCf%$S1%K;3mkH;3nWFkxzr41h=u4m$jawTaHU|2V{G22e1pW4Y&=)aY1$gyMQ|h+kMap=>_(}@j4+pfZw*(JJ!lVt_I7@180GkAUA-QfYXti!Rg?+$O7<Oa0YS*I0L)@SqxqPR#B37Su4j{Z&_<OO7bd{<h97f;I-iO$l2ia;C$p9a6Wh|avpdqcsp`FcssZV^ON}|az6M?@Jy8C6y!W`3U~%`4tNH5I&wC6I(Q*+F?b<(De^7wQt&cl4tN=O1#&rf1vnSE3Y-gm7r7SvE_fqyJ$NH{3o;+P1-uQp6}%0+6S*C{6I_Zc0+)h!o4yCTQIgA$#o#h<333Ox1YC$L02hKS$jx92coT91coTRXG7r2Cyau@%yav1y`3`s`I2-vkI2)Xa%mQbE7a^B`7lD(J>ELAW8_2ofH^8aL3~(xV7IFc27B~&5f<vq|)LKE-im}!(YsH}?4@L%o2ZIM9hk|AH2M+`fK=uW{g!D)D1<UjW`-A<g)evci^ab02jhEyG$iCpdICcY+<VMJ$;6~tPD9O&q5U?}29ZGT}N^%%72poj#6^4==fs6sm91o5Fk3x<Hj{=WHNuG!t51t5)MaF<*!3oGXZ~}OWwO+T@G;2*oNlrpe0Z&1H5^^v&2|Nfn5Ihjy*FnPe{T_sR$#g8qfk=OFAUFW&2Mz%D6SjMzA4>8NWK-}E@Nnc)V3}^<;ouS0dKK9o=>~2OZi9RZ+y?w4vZ=7`A0#(HHWaq~hGYk%ov`gsB-<keSiTwv+ulZUV`L*?+Y3o{L^cz)y^~}oq_eQ?wIsJiwiC9!nPg-CCV3<>5-c+eEHeTua}-$SSnx=&F{Wf=-zd2=aw1q}tg!7lB^&!v$==8WVcW+_?uDEJmN`w>_P~;jeX?X9<m+I$?~;4&c%%>52R-p9$%)9RV3~p7MDWYV0PxFT1=$ZQa|l=gzk(bNegzzg904}&*HDz?*HDt9P?E<W+k<632bSpt9s{0$k~|6772FlqViHR7WMm>Z5$8M^B{>+WfEAouFiLVbG87z&^9e^u9*2wqM`7OMkQ2b;z|r!v!|WP3H~dfkVz<3idic!$aR2Kk>;Kwm{-me%p|ATTG<=x7e5S1rY6JS=93yw{;@?+E&S('

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
