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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6a834c1320c245ac87d16784683aeeec/part_001.stl', 'relative_path': '6a834c1320c245ac87d16784683aeeec/part_001.stl', 'source_sha256': 'bb85ede6c2d0a769befdb8d2fd6ec30c287eff798d03491494cbedb831b2daf0', 'input_faces': 179, 'input_vertices': 197, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.21716272830963135, -0.1362570822238922, 0.1252908557653427], [0.08263472467660904, 0.10538265109062195, 0.31724679470062256]]}
GEOMETRY_BASE85 = 'c$}q~3shBQ7RL{uDVc(T0a|*}c!;7X2tE)Fg7`oXHBmD4QeX+nTSOE+M5!4MQ2`Z|OCo|OLZB!X94_Dmkx?F%jW}Utnp0|~Ys_?-@9e#=bIz=pwPwxSwf5To?|1gy-*>+Az0SQs{w94aIsClF-7!0x{CEh*$@UUw$t8xzC9HWTJbrvs%tj;59Ju^3_&tG30)j$}xI}J~eOP$>J8|~Yczci4Q|!m__N$}g65>LmRz=5!h0EM8bZvY%<MHo>#)Px7!^ElX<9L@b<M<T*fBd{Cx8Ye^TRn4<&#x6;%=6bhE_*3BS8DgET<#4_Y?r+-R1aL-*$3h^kK7?%xLt?w-GP-5-xC4x-0p)I@0xQ`E{nx8JCs}~yIKwPK6tYguHQR=c@nRdLEJ9S4kZ`%eO(3l-BzmN#o>K0kJE4!m&Ti%hWJ}nz_q&F7=JvrR4z+_zjs1Cd^XnmQ}r<@UwaH(TIq%Hl}?!FahM+J`D_NZXX}_V&<{~7f%i^y$9fx&0_T#iH>vo}<{Id)DJ{VHEiYpp;|lEO;^Is2y{Q&h@2O3|HND%~lw2D9F7$&YA_KUT+6TFH8}vUPkb4QQ@45*0Ri6+2&&~DiP;#+L5AmAtY>1cinaH_sp#P;w0>lfp8OZCsF}`I5Jm1~}+mI)ohkg@Mo^+~s{TAqF;g_c>E?w@2<ELTqWfgD#O~tvYRLtYz1pUB23Ws_{bMd0G-?Vc}p#4JIX5<k`s(v$Y@x2J>H-2Ci_NR9u^6NdwH;1+=xuod_<4O}ZLdC`V*Q%A{@Ok`M)6>dvD1^jf{~zL!r$y?OTx=Q#<Afiq0WOZR!+6tD;8I<0lafo8mtg#eDQ&=|sJ@tImJWDt|3Nw>m-u^Uq5a?8Xn=m2;@t}I+p~^ByDP4AsrZ#e@EoPlU20CxSGrjSoX_<_?(`V)NU^2BHHU@+7ve{sgYSQ7+Nk1N{c7R<9h-GZE;h{tuATn9igTUG$PZpoalvW}=F!#x7nWIL{OSjAzgmZz4N5NbPJ(!8LW7Enwr;@1-+R=&L<5|+x}fI9vA{L4UjpYWhGPD_=(Eb_qTMkFxh@Z%SL<<{?|)>rK%UuEINuNZz<8Dtb|8<t2J=fh=QSMX-eZwR^<W<973_z_9eTLmMQfp6X=FR*Z@q{-Wv{AU@yTr9Li!n;FSlGFKOf_byyh>sZn#=vdpf6IfILsu!gCh~T!rT=I8OsE+8u%CF6Moq=9dN(0}m-z^MWrhPkROM-gQ|`kiYs{<la>{e%dmS->@!L#!C+A$hV~emj?T)xR`7V>x}rJACAxSj~anb*^A@$U<a;0>mLB;Y;!P=SwNSH_uMT3p0)tn({&$tq{nf{@70C-#hD%nxJv}`rGEl0T3ka;`-n872ji_;k*9@Y{*2v_Urf*=Zz{p|*zCgg`=10ZejcOFUs5J1=Obr!9k`}$ZXG<w-<olMv<hic@pYBBKkf_z-s|F{;+h{!FT%LE>jhlgo_-qVn>BF3OLrdH`SodhE{kV&L;X+ckpGce1Z77D;Ns0n<ee$de(u}uPMojh$Q^rB{iD6w54be&K8#x_&Zt?%?>OT8Dli4EG5vcjaPbXTXZYI=jVit(3%F!C5&25}Ik>NupKzV@o2*lDn(u~ngSTk{F0{K~{+_-%6+e>=@tpY`Tpu=UsDb-Bd>r~gh#uRm;z_O0Z-U+zc<*iva<gRYhmrxf-kP}~-}n&s%{~@5K0S@9p`D!?$ioFoYF_J(<EmAM^Um>M739e@!v0Sh3Y@!nANhU}$4|W();o6ZDc~Ni_}tCQVE^I^Gk{B<+y$=HpTqqwDIVi*t;74uZ|qX>%f2NzJ}+SY$kuY;+0XFY@>_oxhx`p4@aOyHVjJ9-Gc(JT^ViT12F^JR#d(owgZUe5PC`8GU*dK<=x5&D0yy{MCS0#9UI(r{@e*>47TPIXK8Evd)C<TXN8&iY^$E_?sGBF0^-8OT;rj3(7r4mjuwLCW9Ovs_Ers~__n}_ljBU4yFAu@zzRVuE#vHiNV15?ok$JO<ANI$6E!Z08MZ?n)sCQ!$j?cIWjY=*BR{<9a+<|lFk70c95WFu-+{Z=dLgaUfp&vwT3HI|sr()n?7jb{*26Zbr7f^`pPcTRB!6T=2o2xm2`73QOPr^wYpN4Zn+?#pW{;#lqtcG+e`SWx5$Cj9XRRG54#o@SWX~TBT6EObBFWAmXJ@V<kQP2<bQ*k|f`zgMUB)zo;_)o)uYs-E{zIomf$iJ`+=C2evqg%<jhgSG}n*)%i@0$aBX5V5}dx(n*Z{xU1?LdBI{xpbp4m<&QXg%jdH)kkEr{Vj~(+jxHy9Fh|_q854UjpypdBCbE8MyEjo*#01vHhNt)8P7FJMi2dD`B4T(I0>x+Yh+#@;T%+i8~=K#~0^ylyj?+i?%lSUeh8VpKp^6@p+4IzqtASMI{$6Ov5|}vw?FxlMg_=#Vi=Nz4^nNm7M!!E1pa3Mgf<GtpG0E&Vg|&rUf=CIoEsz$8$w6j%S|@$an3*ec{Oxosx^z>6mAgvx;+jF2TBOI43`kU;YHohxdmdzqhae_^EuHFLcf^aBjvmoG*rRQKS~QR8xTM^z?63a&f^|cpe_O1lup3L_X{Qw4WdBgFL6UKzU#Mp`|({H|%Rdkqh#r+qIB~&I!^vN1S&zGLZZ4!THi@i|d<M2wb>32G4;ZLc5Z45C4YmS;32dYhNruzS#-Kt=|QBALMh&k(*eTL%tvN_?|fU8S;=h_*^_+ZB}x@Ee+SPNL%C``a+2NS%>pz&6izD&gpO9y3uo0&9{YO`^8@`sq*-Z!};=O6a2m6hwegU|8O6V#dBlKwL)e8NV6PpKmFh~aA{`=z7JOSZBue_S0bLH>;~ic%IsdDsvl}wI+R?fFvfOno71j}r+(HxUX1V2`yXNc7hIvAxuPcQ&!pw}p0+;)&n?p?G%LCIT_Db*3I`Q8^z-w1XBB-^IX=ZG??xpTA|)K3`E!Abh3heYkrwj@`{Dj#zX;wFgl}RR>gD{V$$0*$y-}^=x1UK6pKgCz#kZSEUO}o~&DwsQy72q{94DJ8XUVM&Rs3WoL-}Ly|NbYlHLm~NPiF2@|KFd?bgT_c%o>?}#B4XSousp=Ec?9*y@$$sN$(<`MLLUe81zR}&Z4-F$Y+zD%4`ZVPx3QJdy*E&dyy7MPbWW(^mNiw$xl&eFDiRcE?G}t=E7_|>B&@fBkfMwmCCZ$P>c)dP-ch87m(MG){=jlyoU7Kq}|B7l0L?)nDWW~5NX-3B7K;2D0vUkp`_(@jUn$q-h=ccx+nQwj!+%PNFSwgK9vuXKSug<W}h*uC*MF?&gsl-BITVxY!YetS}?OE%-$fsm~<|)9A;~Y%W;w9*OFdKF|yvrERVjIM?9Bu$vI=lN0W{ry^nkz>6Oe@Fnf#qa?%prQxS1FE`|IS(kZ0#$sZ)0Px=V?BGN^a^9a=;*R`4aCeoWpA0WS<^a0YR$d{8oMY@js=cMN{3uHE*d;sYnW($ZdARb735i!{>B>g6{5Mm+3Wxb5qQo6pBuE}~0v(?NZ$cHO*7?oxJ4(WN+R)6yIN&7LI&1@F=Ii%-M*`NG8(xuEwn4KnHP5LC2PmnJqeU`4BCx3$U0A|+AUL<crT3*s$VAhB9%TzXIHjKlM?1z&!V)hC%6Y^H1W0@r}izB~*^g6m0MLv$S%->`7F6k&Lk7YKFnIm~8(leR)F!LtwOL`V*Kk`1LBPib*((h7PZd)R?Zv*M|WU`JYpFnyev#rdM$%~|SFx$rLL(<!+{64b}n5B|WBc0AHliA1QGf02RtcF<?=`&O|<ob|&D(OtBD}($F(uTGslTM(rJci{l8Af^;l`WVJWoAzPRnmi*jiBoz=$foY(zPL^M^Kq()|Xj7(xa$6nwh-)o05Kw$}cf{o!LP0wxsQu4Ps_S+K$TSm>p+UOTLVBC9_YMRgf<vEstCIV?y4Dw7h=GYh^H*tmSn#m;65RF{CXN{b5e`ZRnekbgv`neq|lxZ)9v~@}K@z{O3oM8>IS^@n65GK3XZi>BbuM{Gb)&-&dZe?1qhDVl9zpBliy|dDZ3'

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
