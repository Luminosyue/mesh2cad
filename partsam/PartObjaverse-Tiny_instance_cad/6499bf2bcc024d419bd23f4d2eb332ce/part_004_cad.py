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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6499bf2bcc024d419bd23f4d2eb332ce/part_004.stl', 'relative_path': '6499bf2bcc024d419bd23f4d2eb332ce/part_004.stl', 'source_sha256': '3fea2585fcee458475286b878d2f1bef9365e8e4fa63fde9719f777d699370bd', 'input_faces': 252, 'input_vertices': 187, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15709377825260162, -0.021845325827598572, -0.4410935640335083], [0.17685098946094513, 0.18869690597057343, 0.22239916026592255]]}
GEOMETRY_BASE85 = 'c$}q~2~-qU7KRJZ;2tHoA!;cIF1X<aF3@h^E~2Org+@g*Dj*=@-Y&R{AmAFc4Qc=tH3k(;Vk-)+i6$oQrj5o?6OB&J=p>rVblv|)yXMTCGiRpHdFTK5`}TeJ-Fj7B)r9nSD(9-;)krz?;{N&yE{dX!DvGO;9G#FfX<T$-tJwIN4oY?LwO5&D4hkC>^1g$TtjzWvADuWZ!Mn5S-F1SWw~y*QAub^)Au2X9E@6DM<_AShNsPAni4&vZqiugTZR^*`M{U>4N1dzwkFQF$64YJwP93+Yp<(rdfi^YAc%RqQdieKZ@#lT_iT1bp%|P)@BYzX$6t+>~jn|yTHy7U*Unz_f-`dwhe6{=!;#-{BeJXyFU(QLMv)ADt=us$nN}h<XRKALN$NnaHRJZcT^W<yfue4S2n0x+;ctaBMRB|n}&u=U@1$EZhDfJuo4Lfh|8+J^QJZkDQ)bk()`3JYcym_AIb^afvSl3Y}^ykFqCne9CK*?{-2!WqhAim;Uf_Wb|5?{G;BVXzXJ-S=`aSbkLYIvR_zS5&~kIXyfsl;1eZO@Z<|KIZ^Z+?G?x4!?^T=55-mON^2H}OqD-tdR+l03!@FHlc%olTl=y%$j`ajgg4lzz>r3jg#d@eLl$#5bh<yirr*icrLNNfh6@?Y#KrU;2n|DJdtu`gs=OQ~cojtwSDbsQ9WwQ}|8q-H<$f1sfz!o!2Ge=bjedXgRQ6-gnMKJ%vq>r(_rWVYA>@a1>wpI$eBY&&}{p^b_CsXuSC5K4Ic3Zg(ZWMe!G3Ey+eb_2aNEkC*GjU)&h+znzkJwYx=pW7`FYKera~8|#U0UOWczMF%nO`kq<he|iZ1DR0!j#ZP>zaU1HajlNlP8;h?#`vU%@0pgpEI%L_e*L012yZmjYXhIR<Z%sr0f7vR&njVaKE0m(2RVKoppM&`2*{CP-%eBZe5AkOTktgX~y42tEJH-38K%ZwFPuJC%>Wux9ng@UW9rPz{F#3>@nU4Lo5&73YK>u@Nbonitk`RA1NPJ_%7_7JCti+pcmxDjpg81MKsK2k{8vEm}bSy&O_O4nX^EzBdo?k2Jd~?_{<ayRoeDkG#i2vI`tgHOv8}`2H`x5c5L(!kgx0lPjFP>uFiYYjbwMv)U?-M2U0@gdRrTA*jRpcq$jP?H1Wtq&==>X>4@fq^RY+5Amd+wI=!sK7&mefBlc9H$OmZ)ks?S1p(a%UvInlI|f?jgRq@(l7PKDnXuODjvf#cc$R<Eh6Bb?3!Lm#}{>U4g&S3GrTY(6?Gc#J8q}<NW>jU8&R9xQqDaYmbrVn{B9b_4Eajr&=+Ni;D&GdPdHcJhzVM@)){@%#`?tG4N}?C%$#7IR$zCM4tIBH|>3+qpQ@Z-0FxvA4*EG-w#U0bDY;dy2HQYCh>-c;i&WVvl;TaZo81*as|h+$5ipvUNz9?UMAFkI3wA9pO~KKVBW}x={TNWp%34mLY;rO#7Tc<oW$`xjddAvUQd?yJ>tbz7S|Hrvf#{k$+P7L<d1l9!`?UMIpeqtsEzvf$BS>?QXh5ZbwNGf*Fm0Z`_PB9>*zzZ6XWE4HxI-Y8gYC#6^#{teqH20kqUpYW0dIBe_&l-<Rbsi>muyWYs22N=+EN70Wwc^iLA?TuQt~E(5aWicTd9c-R>s7`H^Li_O}{Vi1miwxnb`c-5$cf`AU34?dl<ccKca5=Z-!U9T(qttP$!@HsHGPXM<4j{k##sC>qzdp7Vx^AK(su%?g~4%~yws@8bx+YXR1^qyNZ2yM1Mu^(FU@cck{Wxp^)0VS)>e<Fw7jK)XIz_PgVJ`SGKuK)XH|;u?yt=6^O#*9Ttz4YOSnWZt6>Fz-kQ?5lBx1YIA38)ID^HXuG+#qrGvLLc6FhWP7E(4T#ik>_c>#6bJwek>jFpCyW4cHGOp@2oqvA^!dq)bsKi?2`zOB$>C0OR4U-2M-qCv}ffG`CR4<-2c!wpNd6)x_av3)jB6|Ud(HRzU3^OE_oVe?vy-V_L4m6!@J4in~v=g|71h)l}_8|%lpeGAb(LaTvr=j6yG?rKzIE&rns1-eqNUhue@&Q{BC!3--Ak2fcR=c1^CALs6T9&_+{5;OJY;>t((bY-{-RLeM6gdi0AoR_Wf@5+=F>@FCf3?4W0kyd+Ns`oo~)@!Et|x`!OZE%1ZGod!Y{<TVsC?N*CW4nS%AE_~3ebb@D3l>n0$7+h@3L<Q0owc3+`<QWg1^lwU1%wkU-k(i-cURZo0li&e;@+(jS828;jZe(9t|=NqGL=)ZqQj1gb;`Wo>yx9I({`;a5}URM3bW=Njo?@o(<usx1r#iQa|&o;%r+Ubk^;B*@CQ!Ad5KJa_l@ZgpB>aiB^d)$Hld7ri7p9mLUNqCLx!-7NN8}E7GcvX9e`<d}i#5Z^Bg8Fa&<)*!FeKZvDX|AY$VBJjdk4MAbTB`HS>t?|B!S|iHOK14$3*m3yq4U)XE6|^1qflpu-iUvchI+E+<9dGiABb-{Q~GAIcE)vS<)SR{=bT4BFZ*Gi7ymt5d|uy7kN?2^M!x4d$-n#-{GzAGzp*#`%`dRu+;H8tES&(~#ToTC{|ftR&K&WLkLtib(hYgy*NR_u-)@+@8~yxXi}=<CK3K2oSe<X~+6L=wv=sem&}OgH7Z<Qk@{MRO*A0s?M|>qVv_R%}j}hM(aq$bBCwJxf&g^Bzb7JwI@QWtmc{%@EJjea+ep37wqw)Nhu@cX-ms^Q%^1TVa+Hl0@J{SMZbM*Xac#i8-qge7hzYYId4?I`;x)<BWn*);Id->|(%`>|re|T?Qyj6|I^Lyejef*Zrm^U?6AJ6ApQ%-^|Ufow0>q=Uq^UHo8P@iY%@~FoGQ0J07eV+Tz<$2r^a9F=C{w`tMUlr%unc?yrqioN+E;_pd{GA)bH*CEiz9n!X{EY?TTju_R_~i>^A1hJ*84`cn8|SHV5&ro^dHygR_rP`U>K*voBINnc(C0nu^Sv!_9r>dmTjHC)i}=30pDW3c`(GvI;x*ZCRde7Md?mgq=;v$4Lv+6)or<{X8B)b|1+|TeimNgq%I+s5&D36H`tN^2n$-Tk`U%OmgYW<Q6H<9w4Hay|nOceLOn!%2g{-L)xg6Dz>O^)Vm%TK0pjIY3kSkKFkt>p`Qmd1zlHawB8dMi*b+V@Kku^;uYnniIA=lv0IF4#2$C0;FKO%1@=TLW&bI3cWACq^GcTw}myU4lJ-Q-+yK6NiSpS*`!K;A>%N8L}>^Z>cNZFIAZjvN{XQu~kt$^EE9$^FP-)Ch7IIg&bw97+DbHfB?2Q74gSk!NyfJdqkfo=6@;9ZDWU4yE=XhmwP--N?b@uGIGAuH<&q7UXthAKUPxdQe-CJ;+TsG;T?4Pj1g%x8%^cHHXHXsDb28<nGjd<nH7F)G+b@@^ES-c{tff{eWyFPqsTYlQ}e=XB$hY%c!%-%g9Tpv&c)xi>Ncni^vN(G@e17NS;BCp^hQPkVjKP$)m|bsKMkR<i6Cd<i6wpYCCcOxdYXQ+=1Lmd3)?zacJyi8x5%LR8O)yxgOPnT#sCz+Js!6+>k?KZ)!`jrme}|<YpWix21L>w<Y^iyOaINJ*fl8J;?*9!^s25BdA952yzs4GC7Jog*uNsg*;bzySL_YXq;*r8PrVbQgS9ao4SmgP0pe&A!m`-QWufelGCXR$s4F?)P>|U@&f7%@&fX7Y7BWgc>;Abc>+0{I)off9!Bj;9!Bm@4IuX?8>k(~2C^Tu71@v6hU!IbLvE_P-N#KiG*)fHjarx5fLxbco9a%kO|D6;N3KbBrPe3Al50^Ll53IcaA@3!>P^<P8MzU;F^9&@scp&4$-Y#7vM;$awI{hVxfgXHxfgj5bp&}3c_cN8Jd!+?I)yxzJe4|^Je53$no6ESUaY)5PZo1%yv8;*Qa4jG$eYPqsF~y~<ZaY!@;35TY8H7b`9tbj@`vP2)O2#$d9{gJMAq~ud9`hPY8$Jl2g$3*E2*E5yVyo=+vvfeaS(MdIfxuWeV-gc9z`8b9z~9(P9sN?<89-xZ4}zZ5e|(HQP+_Vk=Ij~lh>11Q0J3ZkWJJivWc8bjVH&mo@5S<Q#dq^rH&`ZlE-Ol@9*H~>hz!frTzA0(r&<Y|KR@DPwF3I>^~V~%k}1=CZvCP?cU#Z)9)xnUDmD?%0B@+Ef>Z'

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
