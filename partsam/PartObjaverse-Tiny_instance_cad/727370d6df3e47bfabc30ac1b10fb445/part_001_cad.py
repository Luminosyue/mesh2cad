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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/727370d6df3e47bfabc30ac1b10fb445/part_001.stl', 'relative_path': '727370d6df3e47bfabc30ac1b10fb445/part_001.stl', 'source_sha256': '02e3cab5508caaba7295a2b37c081cb21b96e373d5dffacb55216e7718747d30', 'input_faces': 384, 'input_vertices': 315, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10558278858661652, -0.22740766406059265, -0.4190961420536041], [0.14329099655151367, -0.19935041666030884, 0.417163223028183]]}
GEOMETRY_BASE85 = 'c$}r133v@x!^bD~B?w~Qt~Hh*h_%SnTVkm+)!J&iDp9=FAg!%N8)`4L#eVHYsoH9*3{^`Kgv63mxn8`AzFJgOmA-e*`As@=&G$Ut^L=@q<Nv$AoSZpxX6DS9xsT{hIdcUo@~5&=ebnK=d=(YND1l0_5+55kX7GU6(e;Lp92cMj32*$Exge@*=jfgRO1v^5BqnzBfVhwru8@`kn}vkBLI#eA8xz-mc)t;GF|mek*MI2fSf3v~sQ<`V-{+c*8Z-`dHL4Zrn&kRF{uJ<aK^>R(V3LvPw@w+Ux9XJ@VSN5Dr|`<K#>rN%-`{#bc<=YJe({OYKiVYy_&Ui}?~aKUUcH+x>T7pa*t`~<VE3IT?G>LFloIW@Pw%vOWqDCYuLc}FW%c@uq}`$)Id$P(=e`u)JNKaQT4M2JN58U&&1?C4%XWhEri$$xIB?NOPvIWIE6sNb?>@NS<~8*TXTQCh&8yv9vi-K7%l4mlzGU@U=e3Sr-xuZRl}dl5SiQdT$6cbG?_Lx2y%E=KUa#{w#p=ClZwjwOds3ae)_s}HyT8tm^$Qge-Zi0`*e~r+n(%6aeU9E7H-E2h>}~U|*v_(@)$a<gxA^pe)oZzn+q^oYgKVePVMnjgAJe;2p6|4tSFQ_R$ny%XuPx~4mHdZJS-rQ|ap~(l665I_G~==ur&33SSG%lAb@IwPiH=@B(Z=RI<)3^d+Id!19`}2>MgR56kA&AM9e4C<i0<f>`Ujl-q9Hb~%vmjc*A>ER^TRT&UhBQs*(a-xUJrYaV)d>J&kphVel=Nt`NRz2Ggk<&mN?_+l?o@FeU)R*?MxqI^ZLXJa=TAY$oc1fqMSFTlo4K^RUz5QoAZ+Cz02!vw~a%_w_?9cZyrZ~Z=NTncWtb`-8Rmq&vA8|=>N@7dEJ#MEBfyayePa<@S>yFi={c&FP-Y>)ek4yyw-dC7EwPdTzF67*Xbe$#z`M=RbEF+_u74)EJv>u%5e1h=mh6>CWnY|R`X32<DBgisyce}{$hGp#qyi2<L@cmEi1|5v#--q-Gz784Bl+LPR;tJH?Py|cG`M3i1vTGCH=klbgNfiTyym1_`Fnq=uAhioo`|DdQ?$apZkI*V`i4so9B<eSM~OeUaRpm#p>Nvqt*y-_P=$LbgS26<~e#LMPBc&R!xQ1>b8^q=X<vLrq3QXvz^I#gjd^dl=IJLhqG+nybt>OgRjf&&QG#=t@85}o1Z;pm8jpepPbJVs>%5ruSE28^y-HEHm_~^JyG<3@NBu=x2wzj!YgSlg;(CHA-s3~_$Ai<Yg12VS$+2P?&tNR?VRh^dLr-d38&<K1#Out>JOhTw>u;_-RhMK&1~M=A#H}dzU6%7`QUt(%`<QNdvo44y(ezR4BPo;`U2giiu#wD$o{|MlKpAaM0jn~G@DnJwA94shYRJp@x`&s2#Z(#nCs|OcZBeYBE6PB*9YP=^O7s)%JbrLuVe39x9jc{nr`)GKePRd*JS;l{v*e2K$r72|KN_JSD)UndH2Jq@xuS`RL*Zl^V+;}>ygdtvm?ifd}Rmo@Ue5^@2}>S{$&2sPF^{a+tF(m{<5{Bk3BV7{GRoIK2nqQPs|Wr|Ek<+C$H`=;pmkkMQmPKJ!hn?KcByC_vrzSUe9`#>gZWNo8B{X-4L-~w;#ykd%dR3oAZpnH|Lp`>i1b}^XmNCvGTlRJ=W@an(*OUV{F^?^V!?=^Xjj+?Y=_Y0V4Y?Wc|M?%jTI^U-HcV-u<iXzS+GLtM}F)&`<Q|RXJ{+hi{4PddJ4}75z`id)mpX9G92;<>&G|`7Yk(&Ew@?U-3S1tZ$y@?q!Mg{xF{Y_08+fzrH!1{$6KZeW@Leqq=md9RIYYp|<`M`{u0Gt9O5v$15nw=5?-jf3NgdX7l=#Zrvl4zvmfmtBf<EACX;q7+(4Fx}(=}UUBrQxvs-|XH|ELc36+;fqmpU;l_I5v)56kFS=%cs6R$}t!4$$j(d<RMr@b+yT4aipZI&7^_%Ivp(Te}`>&RaIc@c3|NXrdbl%bH@gK?gGkBmpA7A8-v$ms!PffLYvmJl0vc7$(KI>c4YqQmOQNOrcCu?2Tr`WvNj-S_g&hq!lw0N8MlsYs{v@<JC9>+HK<T~QpXTs||*Z6yl=Nf;nR6lC-YSjCaMEmoG%k73W6yE!Eukd==WJj-=&qsb<seRbywSSe-gja9L^~Rt7l=IKQ=F-16H`U2&tV8_0o*8cQ`ibBKQJ>@PNu8T+_4<{DHm^j_`$W{=B;OAxx2GK!^{ej?UTG+w>(x66Hm~!Z!QZRQlcrZ<YtI(-i%*dIpH)VzEA&<!rQeX|=(TOhHt(L;aGvmoJIZ-xb>>mAo%h-ZuXNbx=yl$=_<NOk#`La^mFEl3`cs+lBGc*>=AW1RwJ>Mj_IirVKXD6h&L^&3x6`fOoPSL3UHHyo>wbB=M;@|zbHDt(xnKU?95>Tzt2ZTz`sRN9sAgEb#`?|l%AV@W#C9XEiT!eym@oFry{7Rp>-qVTXMbPv*X!B5awKkr=nwnr8uk57t5@FiIC{;zU-)^Q{WZNdV&@9${<<eD%CLHKf7S7erJwNED(iN=yE|;N`EDy5y?RJKH@UaGDZKYYYmaE(T>sy?f7$A@*Z+9sa693%*Z+P#`}qRzTHV)UJ+C~4?qyhg_In1rTK2fd*3Sty*NgrKossQFt#$O~{+eDN+Ifwrzq^ZUzvb`px$)huYplmnjr_&t&Gxf>Qik-*8?K`HR#|=a`QYcZFXj7Q1@DatU27YMvHdSty*Uo<G4I-a&p^4}+dblPgtZ-a9!Ia7*qdzgdxoqNzV&u_KJ0m29$&oq{@LGaySg~nFO$>e-CN^i`w_H1rtng$*V}#W=#_0f<hlj#$@_4fZ5*y#mgDgJ={oDUnch9;&GlmZd9SN|xZ{%5o9~(Zy}G`yqt^-)vHJ!~rJpMA?`pC5i&n4StHE)9UwCD0z71l#k#c|a3&9I*p8fUU)x;p-RmRP%?~Q3DyvBQMH8S{;%`X|`==JBNZC?Gk&o<#%ho~pN?IX5xGgf$|qFisNr|e#1z2U+uD_07y2DX>)Rm%6c6k+j7a2rRjj(?bJ_1=}4J4O3L<o(OjySKQ{c@lpRUT2-`@6}vaY+i}~WVfiF^s&5ueXL%zdhNs{N3YZgllO&$2;sf6Qum7XAIs+p_4K(lHvh*BN3Xegj>9V{`}T_*og~`VH!sMrdTsoEN3VMa+q^z5>45nCJ^4JM4;#DH>a~Y=9KCMdPw|TD?qN}X@jAIqP5bwG<Fl*Wec|<*^1Ywy>}{J@!yeiF{GLg|5BN-uLy<oFgrD6<c;)w7&i?szoA-v_)<u6Z<^4-vy*JJ3mFr=SUX7IN6VvPGo*fbG43qCmwOy0NXV=;1BGnvM9le$}%jUg{YaJEaZM#Kow|%=4R<FOl-r4Vb+vb(t-DNv7<@XEf)xgtMug@Ru=(Wc#*^als>4<3Cx5#VMRfn`<zAC<wUkO$Q_P2b6Y)IqBOy{qV2Z#UfzCvym{{Q_7xoCi|lfIIVV(?#zOa(TI!T%xeE0T?3@HNs4UxUw+>F{~@DETdX6#kT)2Y(6=BZt7l;21I%j)8lTz2RPP7xFE*3*3o(9qt6bLN<e6fkVl<a41}jtPWR$OOmDFl5h}N6b^z5k%i$xa2c{JTn4U4R)Q<SHOX3VO}GKs5N-gs@|8AZYqBBS8g4|^hK;NPH-f``C5#Lq>%bv!1+qL`0WM9JgG<AKWDz(JE>0GMi^C<zV7LTam8=0*h3k{`;QDY2vN_xW?nrikJHlPbx8bgEU$PI}7k-Z%2)_ppCI1Nzg+C+b!=J%N$Ybyk_yU;$Ux2TY*Ws)1PvkxLCpbrd%zyyNMlrY`SpY5w7blCs#o<C^AY2H}L*|9^z|Rz!e<+fTV(>5I&+sqsZSvpnZTJWB3j70niM$A3f{&Bm!N=iE<md1vcq};v9t#gAN5I43!Q>!#Fg$>K7ajojAiKjo;5U8cRWh3F4jb7Gj)vbL-+|wNqsX4Hk)7cv_#b2&*vQuKKi~+m5o}~Q909A!-*bdYwuDu<E%_?^D*Moud;@L^zeYyEQS|9GG6IfZ8wTh0l^nj3i(+t2GQh$LpQrfBN4}CkPK6WT>EsM}Iy{G*3(tX<lPloma3Z-3PJ|bcOW;MYhg<`D;0@$PcmuqZ`~uzzZzsQmx5GQhUGPqLFZngR7d}WHf)Bz;qz)&+r^saZ6r4t$gVW$lG7HXxZ;&_P8}N_h9r#E1A^8Y?2tOu&gCE0B$lu{7aLxdkxdJ2`#o!>aFdPJzAWOm};BsVnxE$;vE5k0h1{ng^fa{X=;JR=lG8}FMHzu3Fjp1fwbGR8?pA3WR!?npeaBa9MSq-iVS0F3G72r~2X}A>pry}#YBH1Vgr;?}PRCpvg3LXjfBi(R6xE&b@w}YFIP2nc6i>wU0-~wbpxB#4oVsKtx$w%fV3&Q!~Dr9B23f!1%3O9z^laX+HxIgKJ`@?bMC^!yIAy308@C))e`~oh+F)@x!8H&M`$ck_!xH?%4t`65C>%g_(24ooA0B%7xhg-l+$tG}9xFH!1H-tmUdT=OQlMI1t!d1x1a22>LSspG62a_e?V7Lfb7%l?mCUe2L;it?o#$5B1V(_ozZ}6}11M(640KQA!f$ze%$eZvj_<J%7{vJL<o`cW8C&*;@1pE!D!{5OB$wTmdcpv#Sybs<@?t*v2JIF8L9q?xI3wSfUj@$^ZgV&O4;I;4qatXWuUP&&4SHi2v74Rx}7C9H51<xdBz%$`#<WzVXJem9mo(xZ*82lkQ1^y78<SQTe%6MOS-&aPH@f3r{k>lZU@I-PFJQ3E&DX<2AOeVk|!=I4T;ZNY%<Q#Z5yp&uHFNGJAiSS~0A-M=%2(KnR@M?HHxdC1eZy~qBTi|Wvc6b~76}c1s3f@ERh4;V*$b;|!_%N9SABInor{I(DSuzbi3tuKP;mh#9d?mV5K#t&?|I>eg`1?l-F#fgvhY0__w7>SU{$)E~TiGwcqC4d_?t#9Abq;Zp2{7J1DE|djH=%a'

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
