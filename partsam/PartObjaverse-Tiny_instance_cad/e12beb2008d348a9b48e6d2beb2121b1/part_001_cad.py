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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e12beb2008d348a9b48e6d2beb2121b1/part_001.stl', 'relative_path': 'e12beb2008d348a9b48e6d2beb2121b1/part_001.stl', 'source_sha256': 'a8d98110184b9164119ffe35d3d5ad921390be5ff48f53b02c68203dc684a88f', 'input_faces': 304, 'input_vertices': 192, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.108498215675354, -0.13362805545330048, 0.053965844213962555], [0.0752057358622551, 0.4295537769794464, 0.4476211965084076]]}
GEOMETRY_BASE85 = 'c$}r02~ZSQ8pj(EjW-G&sKizwcyk%$kkG+IO%xpw<E@Pf3V4E|5s&sFDj1K5c%T_YP*gxgRMbExC>qIXyalgb%^f!zljxdMqTBC#|B-HLwrXp4s=oUF=Es}&UcWwP3d=yp+O7hBwHJJ@1%IqG69iTb1y>;{I$=)ir0B#RGiJT-AUKm}FI#>zczC#Fl!K5YBzsMcPMnnB6(oA~i3#xPCVIupOqi1pHDkiegvrs&_lugA7_IxnsZq0{_4l281O2**{++vti^Tu&RiDjaP5G%(Hl=P`53#gfm{bwU-ZxJ?$=(Z3cjl45=Y5rVtJ}$9_Fnupy^y8!W@<ULAJOLod#{a*zRBLpcmH|B=#}(x@=^`2by|JPo|mJ4FnM|Bug7V;?e63S_xmO<f6&Y1r5iWND_6^CT<f0mCNDUpQF{emaN_>u{O^5k@-OFO^X}`&t6pvRxZx*EUT7X@^3wOoyq~PD)W72R_^8pV=W^|O<!LtcBiHa+YmZ8!*J68`)<;dhWAe83v3co53qH@Adud$t!sjM$>tC42y}G%DY5p(U2dzFv^L*ZpuUof><3=wg9OL`FhL;l`-m>RKhXs{Jubu77`<KJ0y|ypV<W*&i$%}`B$y>W*^1r*JspQvqn)=t4bfWf3dr#B+)$h0$58WuD&tEuO$<K#hPSCv4%E$|2uF-j+U9;Sv&-tem8IK>e;$X4SOOADJ+4IVQ6zbm!F9?a|alOycxXO$u?w>y6{?K34-WnCg=M%D>uczO7leca-YVzX0Jjly0KH%eCTEzXM4yO4lu1mRp_WY=6+|n<}E7udqi=N-`^XvNtr;T1JO1Wk9@=w!w`;5E1pT{l8Yja2N{^!rFBLDdS-oCLfdCk2IKhA@GJZ1DsLQj(yCpeqtqdvRGePm<ug3C(2{`Vh}7nV07FSol-{fNW9A+K%zt<X3h@y)h0A7Skm<dtMMKCVw0Z-0LRdHHb+zn;{MFEM)S(z=!QycBJr{^go}(Dx=Uo(tpS#tqs}+Y#`?m*k7Q$qRqorsGh(>2s0%sdnVG=iB&s6xOfA=#^nd&AzynX<T8RKY4l1izBA(@($$lY{0#6)`|L2F9(sg_WqN+60tj<vi_wD<fF^TYfp-Jd#w>~KctkrHEAnf&*0|dm9sm^OLb1s_R3u!U7_}+MTf~}SMvD;C#gnnjhJ0&&#Uq$Rrb6zJMy;C%k{I!i>{e`URx^8^7WWcULIVJug}FO)#$B}9ZX*88*S=ebcx{Y6DE__E|ySxHJN*<dz5Lr)Rah*7dOwWG<xeFUfehJ;K#}A5b|1)2k)o6E_v&rQ1Z%^vvgmV3Lg~E_<I)9IO2`w<kj_jKS~9?Kc)8N83jf!G<N2G>qPRx>Pp%#lGn5AG=39D^76C-%yZ$VMla<*tg`3DON(wBy_UP4jvH}ZFrR-|jL8d8ktVM+TEvet%h%k8M35J@Eg&!V&*R5K75COZX675mmA{VU-Yt;46jaQw)4d*+(&yf7$oqGHj~_o{gQ>mhRFAy+D3GuJ@7zn5-=XtR>DZQ!`*u0^kDeW*anB^vxSD#Eufu~c$;-C(kz4t8T~ti%t=n_>b`4swkH&4bil6Tmf4(0(W$&f-$Nc#Iia7q6(OdsKW!I}N|ERL(l{rbbjox}al)RA9kFUeUohGjio?!CYf&lW;=#%{ZQnHG?a;ulAf14LaT*;w%{`MC2qt%&3UP!r2Uh#|~F9mb2Js(J3?b4r)U-4lc-w!z<d#Im}(@*pLkan0p_q+dYn$Kr}d>tCZmKnWvvcRqvJkD0x^VV+$+&1~{_jVb*G^ICrE$b$EWsyHW{=<iuy!iScvoAkyrFkB^$&cR!Gx)l0JiUdscUyOUeihs;GkUpMx?L|h^ZS>zh8Lv=W`Aj*$;(@E$qTQ!k=G{w!LJYP%S>MF<x*wzn)}xqXg)ue(|(b!X5XQ|$G%2haJ^0Ey%PT767Bc%uaZ~mbl}(90V;j(koP=WPoK{?$?qpElF!pT?_VIVlt1Cup-ZKg$yd0L7aA4v=e|Z2bezb8SFNS~Hx1|4o7{2NXq}R>(y0C2`t-d=2=YC_kGJ{ct+QJ4?R9iNWAtK7yj`zZunsl6)NhK(E8}jZ8ohYrTfUyVhNtrFKf?QOSnG_*_pC5^b=~7tG@r}}{(a5zgq}Z@qy8z>|F_QkdUDa5xBn$|CAEK&UrK+^dv=ia|H4hnY5q8mgoL&HJV?1Ro%-$Pz|Y?fW6v195*ldN%kvKNacg?NM<y>GJw#r--0D-BPwcJ(w0(Pfk=J}y(tcMX@@Tun4NIoc`zZ}dsJ+LEW7K|LYCJzL9H_n6)q(b}@ZHdO<G8Am7mX{$HRb;28T9>C^Y-A!NzAo4>gPQRe;%Lu`#Gc6@?!XW(ihV4CXLJB?IREJ=T@g)6-F<3j>B`%7CO#_&u+xhyt~Em^(~Xm7`@`R+~lo(9b@TzNWQ6mn^&I5rvBAnnY{K!glYcP&>iH(%~MVDR|iy)SJed5I#>s_jHB&{cjC`q*?c{fm<I9W1Df#lZ<s>sudMDfjn=8SHSI?wFq`(Hu=3Sp>aXpO{Qi`*{fyD8t_>>fdEvwmyIu*HZT3s9Eu?hrz}GE*iOEYXf=ymtynhY#b7wpq|H|-?Jeo&KZ6o=zsq{OCl>UHU2e#JRL^(5+KX=SXrFGCe^U|q(PFMcD@>WASf7L;4GRT*>(sjn#<L|W2!jlQ)1-IAv`d|Nqu46*x9`f2qD?P6XUpak2@9z}yezyHY<67^#(R03(m&t!WsPR0k4Sve~uetnr<T-!dmcQs+Nd5fnKL37N;Y;5Ow0wzs+xLhg`u7Nn>DQ~GucC&kjrFedswcP#F;Rw}u9##mTiXBWDz@i;_0yHVPtX7Nr>m{{9CqsUA#xq~L+}!$0$u{1hnx?d2aZS11jmCXqZr2^$AKp!M<K_7M<XX7$AMW60ka$o9*uk#IT-vdI2b8`gTX$?USJ=v7m9H=<m+ITUBF&QPh=OcC%8R|@oUI-;P%Ki$adg1;AY4c;AY@DD8>zu^}%(JPRROTC-5uC#^6`Lb&-w0b-}ff^}w~kjwr?rkj=p?TY?>tO^_|YO~9>?BDfW}BeE;FBe*-#AKV=rfP51i0Pe5XdwLDm%Yy6=?vFMW6yq?YKbU1tFw5THF!0;Rx4<kTz;A<xA)~;<z!Q<P!7OKiCxXW#XMkBogIP`jvm6N?iESQ_w1CHhha$tkVVLVs<S_6s%!BcCy{7540Qo+60eG2S>-E~8*HYv%@G`VniekJ7#dt1q8h9=^7R7iBaypn@hkf;WL$5)|0Vu|SNMCRuxCgQmxCht+*%s^pcGJrl>4IzvZmm~Sz1)$mU|0Oz9oZJ_4(^QX1nvy>L;8Y!v7LS>#@;B#L3+J|3`d57L$UqghBXRDF&>K?10I959gAWdhg<-T11BMufs??CksH8^!E5!}g3Ly40JB^V&Ia#6G0s3SPD3sQvs?sD1E-=GFGS7-F9gp)#)9X7r=l27LNOkR90MMMwHt{X03Hb*j$+&&83^tV4nX!0s;^g!yCXe>>gyZhjz~A5`g+K?l~8?*+OD6B+4a>CSsUprRA0jx*G0O3S-J|<*MG*gdjw-AWK*H~p2FC6KVodVPcd$TYz=OY^hCA>vvdcu><nh<2WIIF_Cop~y@l#~H{)Pr5ZHE}*zWs`*>k~Y<S67jV3y%vmSe#z<G`c9wr3m0@yH~h`uT_PJmg}b`gw`*669K;`uU3SheGu^V|yNB%%0Z{BM%|BfDeHSk=bCDd%%U@BPhlN$P91+I3LA$Gm7y?$TTp!r?C42yHBjv>jS-ZA+x}{z<c#Ng*=I3oP*2)v)m2N0q;Xv!TZ4bkspKigAbw@XX+*EwMMUjD8{Rhncz&cUxi|vg0zBDz$=lv!7ITlkXhg?ti=ix<9;Z{Bao}XBfwKoj5nef??CPX?*Qi__kwL}or_|8La)=vQsgOcDYyiA5?liQ1jV=*nFG$j{wPK<K91ZEJ`OHI9t0PGkD?goAv3{w;BCk?;BDYdNEy5doQPulDvEI}<UnvOu<gaTFLD)_WeT`2I0U&890KlxTmfd;58MarfMVPMIRe}P9EqF)jsz#57$+k)f|n!HksHD3;O)pA;O*c8$XqbX6W{~jV?y;Y#Mm;>p_Z%TfBM&r>X*Vc)bx)WH9u+o+HCw}iQd=CFVU8PPV7FT@330*uw2aUD8j!1s<mau'

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
