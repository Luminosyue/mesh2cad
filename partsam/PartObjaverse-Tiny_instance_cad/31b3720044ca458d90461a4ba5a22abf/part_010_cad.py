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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/31b3720044ca458d90461a4ba5a22abf/part_010.stl', 'relative_path': '31b3720044ca458d90461a4ba5a22abf/part_010.stl', 'source_sha256': 'eb61fe720fd26815cfa6420c6dd777c3738d54be9575f4b3acfddc2182c65d27', 'input_faces': 364, 'input_vertices': 224, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.007575400173664093, 0.2099228948354721, 0.07000616937875748], [0.11332187801599503, 0.30817273259162903, 0.22561252117156982]]}
GEOMETRY_BASE85 = 'c$}r03v^9a8pjV3>P>~B#qmt4k&<9UX)aPqJR<dq=gG^X;*kff_pP^<Rw#<#N`gq#h<Cht5lN8brcqH6+_gH@cIac;F*C-r=In3(_su@1XV#iEleNC}|DWI9XP^D;v-iH|oR#pf8eTpM|7)w*o5aN1n<@&6dWw%SKQ1wOMoe5%!0fpTsws_#vp=DmhmRf>9$8J9uPpM7jZ2D2^zE(s_L<tt*I)IWIwvtXF>3adIf=1xj1P>8Pm0rd()6ggar&`eU|@HDHRxr3b&2{v{?%c9h_1CPL>Kk7kk6Ug4{a?Z4SZl{>UOm=aL4WT?@|4Qt%)o9Hx^iN+p*NEbbi`X;@aFrhIX8-#x1AwzVqhotT<d?#qIZ(P&<ywZ&#4Uk0S0|Ii<jg+rKEL`u3d*R#AVx$}6SoKXv6>ab?=XYjm6vxSHxcJV{*ryH|k~x6kzD_48V+A^u=`nPGgUHCspJ^Zrcr9X%H1TXCgJ4z;7~3ni}IN-?zK%pUSS@d<v!9g|Y>t+@T^PHM*;v6i^IL3?96KQ8@%&aW9p*L7yD%eUh05e1gqR(t9-%XV_pc>k}Zucz}9hS7Dk%?bHd+<E0Jum7m;25KkkA>A+Sy~=zm?z|OF^=(_5Z=`k>MDl)4^vk#6wtsnDr}J8eaK13pFb=k#ClOaeFSz9UYv!K&JL?Q@XVPAmJb%nw%pYfTQVNwfewX_1&Tn?birY3dD<aMLfw<N*)-Y~nF2>FN!%LfJd<NVsmGe^k!-%^FsV;dPnYma;Zg&Ld-|+R~uH1ITirZIxOyg-kp1`krzL1Y|T0o%{SDe2R*B0jUc5=2D#$Or!HLu_4#}YcmzG3EK-|+AzoA^BW=3br^w=Eh*<LPMYwVB`d2PKB}7&wx++F~DHk4wKQu;TVRgZaMkkA0l~HN_>bUo#i$*A{((UpM1Z!*y-JV?QR|X|!Senz>lN&WlTkYd<9OdH!KRffe_xYZG_gh`lOv$LMh5_>aumLhW7-HH?Fqd&c2*DRIYNnwQDz)Xc>?RW9_|O1!~&8V9jIo4MGZZ7r7**LJiu%que&^Ga~_RHk7*n7Nn_io2Y*<I~hIZtn3x+o(Uk&N19C`&W^~)jn(Z_%v9bXUV6uy<)|c8g+}TxP8c8;_A~wpV0Z08HWAA%*Fm-AMCfC%ELGD>#hjPv*OBqH{Vb4RuXpvEH|ucGZ*XH{k4`#`f{R6u5ad|zN6_C;@U5nhW?nj=#Ls}+ePKY{w_nlCNA=I=YO!9c&+1x@&6si_?x*He=`^3ue>pH50y9X=#uA;nTz?OO|Rpi{$_-h$n)RK#r$`coFeY1xLItNSG@{|Yr#dt#Xex>p5O8B;`b82zl-OansJG)7hvDZ^N%p}-^@Mp|C5h+JMF^^{ZT`TIX_ioxbJ2z?z=Mf8RruZQ#+pDcM})CQ|{T_(unu7(|l7Owz*8@?SqLsVpkjHgPD7NAJtpDos^D-{@Y5P5O<Gj!1tfzPJI8_8I(@-6E5@pGhqu|R~?^D+|g~1;XazVXCFIX%-cz?Fy?FGp68jwo5bDm34GpHJaJNghu$Wx9!=)YGea9uea#u3L3~D6<L^ahjks3Yu|%FHX6~6M*?T$vGQu!E?lvv<(fL{4eEyui#K$4lpSX4=!%*M3d;sTd9`Jp*;wXRKKG$$RwRf^Vey`JM9%`4H9w6R7p8xLL^Wncc$!CeH7qh6o+BKD~YfrAsr1q+9<oizMA{rm9cejJ2Z+y+yMf4Ls&y!nc)A3SYKK{Q(9<$==jqiDXa%LSOer#ZwJfF?n^E|V%<S^Bn(1EY>x9gv<<V~7V`%3-C#I^PO`AzIUW-j(0b<nvZ#N)C`<?Gsx56_|VAJ6Ce>74<mthkszj!_4QyPfy=^Izf4b9CJAAg`a+q*R{IX6|`@F8`Le7W_Tk7xz!+_<F4M8*w!$*Co#fM?(Fhq)&h5*PT}FtQEKQ>3)IocCIC^JyZF-ee^KLimPS&=(;vn2fCl`@BR4wxKf^L#npS0KcjXs-{E}APgq~>V^&;?&EoUnNWgL8OKTE$KAdyXiYt}T7pcD!9h^5#=I;-`OwYCA%8?@Kk5*R5`ICOv<@;j0)rzj;e*J<mug~hyeRlu0wMf42&Ot$(`#!!dkFzpxIdRqA(k0J-O<m3T?X$)5ymiEG=RE$oBDp`>gFBpi^|~Ri3+2E|x%_xWnLM9uJ^gsz&z|w|xw9%)=4#8_8}dAHPV39tSypL$&)Ocr+ga)&?s={=anEzzPcfXQY@+tXbEBDy=SJtd@ALkQKE(Tv=U6ir&#{iwo4lRQi~0V5=V~(-&(F5Ak9a$4I~5!5Z-Mt2I{)Gh!#KD<tV>+m;YVD&FPOP_U(lQ?Z|7N<q5ozs`menZNZe7e#Bg0(Q800}+Cttw-lxo5yiYlfj^XW;`x)+wnTz}49HsGgx}_SPCq4YJ#;+^B+nBg`-&FrJlaIsA7Y*}7^IOL2cOJ=qe@DK4nlvGw^S4!MN4$5Nxp?okrC0EA`&(n;p7(ka7w`49e?H>v?AgZWgZQ3c;^KRPEjo<Wr8e8!_`TxQReWFEu%FK#d{;4Z@m<Bt#dnq8wS(^}?ub(2?(~{vhIwV;VqUq=1n}R7%-&`4IGDK@2kp@S&U^Tm$>VJ1o^ke?&-ax>sfO=wW-ivLRy&Kh_?{!?iJ6OeV$VLtdFDLBcS3hcDeuqjGQ;;qGZ*vR9$C)&lUHK=Zh5f!d8&Umr;3LgzTR#KJF{hDV?|+6Tk%n*MoFJ;8DxJ#tv}t)=>A`Qx((|2e}B52s`nvDkJ)-8LKi@j;1|H#p-bWI@XHa*uYkS>zXE<0^j-MvdVH+M8t5wcRj9KDx)Pr02k>j)w<DO}1>Fe03w{rDC;T4xy$I&hpxfY?roc1Z3eR*0d>Xt1`VqVXemC@e_}%cS(ADrvKY>q$KLFhi&-4oX0r+g_NqDB2@Y(SDplR^?;M1WFcnA8Ij$l3mnhKwaYiB^S;j_^$^RMaAU5}>Fy6|oE2toO467$pJ4U~mQY%q8b)DM0j%3g*B!K-@MP(Dy%&GhJtGMmJDfY*aIgRiMa7nJvqST#L-QPxFb-g@|>%vWOF!Rtc3;eC*MT|{lLHsEccKJb1hdllLiz87-$LkQLtxd$NxQ^DIoyTUg^*$dEi@O6-TGlXC@kb6CZU<z`ti4e>iygF2YuZ{e@5rVyh+-oBmfb~S~J_x~H1s?$I3EvB4L!blTyP_-<It0EQ%KiWig>Qx2+aUyNh}>U52=*LuuY(ZG3%S=o2v!TZi$B3?gExTIlE#ARP-tiPo+uj)9ST1HWl_-4@Iz1*1C4?YMOid727U~34@C&p3VaxJ417bBy#gHu{~~g4h!Cs^a(@mXSWD#Yg%GR(cxPx!_%P(o{2V<d=<zmmB0Q@TiF%P36ER-wI2QGi(Z(G3MF{2>!ZTflV16Dv)5Utsh0cV|gCC9SL_uf3N5RKH<KSc9qoL#B$79TypN#8Gg3g2=gL=ae!@!vDfa4Ch7ves#<L7byD6~BpJ{;N~J{-Qc9s$tTq5a`sL3=MEn6Hm$0v3R}{ot7f<KB(H{hJ8?7Bm<>81>&mn~l+K6Zn=0=G!ZL4s?cZ56{ZS>M>1^kqG9eK<C3VjhFlq9LK{aK;MC9I!p4?am-Yc{5Tvljgb7CIA$6s`A#?vgl_?D4bQX@Jj<mU@*4|32z5H5UL*MC&_VEnP`^3)IT!t6IvIW({F~5l_&4D@L3_h@f^V%<&70PU09=1AuD2Na4*X*HWzZ!`)f!}e5p=#%wPu;01D&Q+t!w5dK*z#QfFA)J1U~{k7}^oOBl;YSdo~{TlxZCNEcgWI4EO~2cxbFrHJ6y50*!>90zVQOrc}+<Fx;o{=*Mtqgi^KknePA%gzo_VJhTP;^YHbdjg+c2%Y0*KbNI&a?V;V^yP<E)uhnC{!q+L&iSV2B*rM>gmFYssZ^kjxdGKs+`%sS!h)H0~ufs9ZQSj{9l08TEfewaeIuM?z4W4OVc&0tznRbC^>I=`*A3g*so^_e;4)upWu1AR;N1=uAXY{y%@*5~S4*r=Qw-GlamZ!%(#BGT=^|*t$C$Y17e1W(Fc0vyq%3LU8{+J$DQGOL=C&2%x$7RG-iG8ZaImBg&9oFL#;+({eBL6~^9foJQ7bEf|#&W-jD3%z@y%KR#Vl4Ojh)RjE-0vdpON`}Sj<_o^mU}6pTw*Nu0z|3ASnd}P1rlSqpF&)a7|Z=U;*`V+k$*nQF2S?huOUuLjOG40;+n)*?za%1ON`}Sfw(0xmiw283NV&;8Oq8~b{BbHNBMP>m4ma~a}n1i#&XX=<VuX?eh85R#_~RbvLh%vg`7{L{4~mhXSrt~4uY|~FQV)s%B~^rB9w=RRjck(<3If?Ue%wSUTEZh%rl>9{0t<Yc|mW>^HC@~%$vP4=@0tV=?7sQ+f9^z11i;^RR'

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
