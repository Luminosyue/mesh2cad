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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/53d9d21ff95f42428225f906cd9a0a5a/part_006.stl', 'relative_path': '53d9d21ff95f42428225f906cd9a0a5a/part_006.stl', 'source_sha256': '0842ea5d35b39e0ff0ec8919b0b771b61f169b5857b2de44044a0ad4c3b2757c', 'input_faces': 192, 'input_vertices': 224, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16946443915367126, 0.14021390676498413, -0.2508455514907837], [0.16075792908668518, 0.46892791986465454, 0.12127941846847534]]}
GEOMETRY_BASE85 = 'c$}q~3s_EB+sAh~<uD|L8IyT1rlDd~NE)+;5lJy6%m@z^!YC!<l-bUiB!p^4wR1icNf|}iIiyJuohb3l!C@E%uh$4;-o5_!{l4#bulKvI@A^L1bzlGg{ylg1T6;ZfueF|Sv{$3X))M{eBB}1>D-;_^646SsmgWbC&kG3*j_5TfY@wNC2`>KqQ{#R7y+?m$Ce4=?+XV$j1cuwW8SLDrx!O4x?52f=&kLV2XL4wGP_W=0Q)Wj5>pWt{l(1m^`h6!S7YBoL4+le(;s5xrh290t{P5Y6qDxPPRehwZT-xubxR$$Rg3Cud!Hu^Pv&FUKl}5aDEb(qB;L7|MaIIoE)tTMph`2TtET(+-ap20n_rPWQAZqvQP;fOP>oDq9eF`o``4iul3$Fgum-1^q2G{I8Gtpi~SIYPCqx!r3z-8^vGx$7jAl31#%m6=s7hG=ZL-~V#0XJ!d;L;6es-OGj0dZ~o^#HiClE%m6-~_JijG{Wej^Kv9Q}>E%L)&S@hYhAW9hQR|JvyC2oqZEdVSHXqK8R~e3vemi{4{v8kaS#c{i6_{2RuN&@_tWnZA3M=H1!+g8<r&Q2Y*;X`57y~O{y=rsc9PJ_jNdf`j5_`KXTb-;-}hyYY9uirQN~Azs>_U{QP`3u4Bhj{c$R|vDHCvC8R6yWuKfyevRWUv>RqkJkt)`*r;|V#>euihI+N<!A)Khci`H!1YDV!4z4XW2Uqf<Dc@>L5&AzcAr0gC<3i$%oxr90uHcHDGu3H+9bEO!Ohx{vcZmn&Qhv^_DY(x0ssQ8nyIPKM&P_i=^Y71me7>iM_z#OP{_@=B;F_V5=Fjschtc28y-(2hTTb8m{YM#S=f=z9$iH`oc%$}NxR0#odC2dTS&eZ>eCHVW8wKE+^*6|u4)#9;KL2Je^1nWVd@1O}QSh#n;Bs})Rn&RqiTY~K{A0L}`w7T5+?R9kJ<Lr5mnY1*f;!<&2cX-Af-7M!!R6Env}+h>PWi4|YjM4-#|G40B2m7}32<qu%~tSNFTaCM3<Z}v6|Tg581#a;`Xjh$h}kw=7yt4dJ(n%&z?1H%$oISjuK0Q&UwQap1ir`h^~CR7rgk%zZ^7SRtfTtw2dUlkwsADyYKb>_25yXv{1(?0l~m_YH077hT_LX34yDweDrfXZN;*aJaC`~nhjj*53$~-5(mMr|A2fyf6Fxl*?M^=kuGxD~9d`wFOvkrVe#CniXM_Euy|}+aDa1ESK)(D|5}q$PY9+OsFdN)B@N;mr?Ig;7xeQ$SHgq5IQijs~W^bhNbaMfhj@nUwhWlVXXv${H6Qy@s;x|&zA0_Ms=7Z_@8&qe;UewV#degde?iuz6#dwtZ)6a(1rF&V#SC&z`mVNOYnQ~IWHOE@YPnU=<w4!_~545XxDZ)5NMa_sm{2R4f*beKzvh;cm+JD})2IID6W<Kc-aAn>^aAn8X;~2lGDd5^pUpyDa(*tvnUtd7`Rr@B$m+V`eL_218urFyp$jFyFOvLl0&1?fMb^QqWnmicKsn+aX7V0=YqUYs>!x7xK%_wlW=35$1bzvs>Z5zt(IrS3y^S7q-T-|+v`;*rM(tOC=g>^&Dctrc*gN$qF=Wug#jGNVdaIO3%xDr$GCHUsu#CPRW{-g*Ge13Ti)lY0o?Ydv0@4J5x@c~beufFIQi8`7u)v0*99(9rv)}SBVtmu0P=m{?SyRF9a*!MTuZ(Tp7{Nvj<Vt$6)0hbg%+?UoN3ge*KWYNAocOvplZOoA`IWM9*otJ~F+tw$bz0rdy-y#;=c>f938AI3uTBoZssojXUWVG9TEx2OJBd)!~IwP;Dz<#Th)f2a^#(p6?FQI*S?Jdra2RA+FK<9<K=GSq*4;x`$Q`#NCzN-9Wz&@*4o<V<%O_zd8yMCbk-SP|cM{6>j{_guCaMM@)upg<_OR*nHXS|4CJWT7%ngPU1)4>fNI#NF^s`&HAg%}6h%st3!b`YOSiO;~5ig9$m?n%Tq4L}{OHVxxxxcQjYt(U)@0}uAXbEITf5Fb+uZaD7`E-mp>ssDGu<x#7NyA341?-KEb_2BBrka*np(omXL*LHo6@j1126S&)FG;g2uD#72o9H#HT|Ht5_{dwTBj{>eNpF#84hVr%DS7`r<v;#Lx@i>qC+#GPN_o&zED8s9<4@m1>Udz|U<`EBUMftg9RA=yuSm?Hn)X$^~l)of~_@>`zJ)h@W3hw(f26X~n&^qkr2X5TFfOxlZS`QCZfXji8)<TnMJ(NPLz@_wHaLqrR_7?}gGJIb_7SYJ(_14g847hs2xQ6EEDyrY299;RLEuKrwI*!)cyTlD;6IOxW2%tK@jJ$w4Gx}kFmhFRy@AU!KwlpjQZ?LEPx>pD;fBaSf`rT@IF?8w1S-9Vmw%|&`PH=hkP3+h5-qVyHZ3(W}E?$8CymyZBBb~w3HlHlTI9&Y<>#_7xD(01vvlIQ0+D`^o9u<NchfYSn)vYy@uR4HB7wl-gs=P+|7rcqjF2eY#VVyNx*PWpAVRg|u^s`MDaAm|b;xPm1{LnCh_}{(h{P~NFd8s9M6W=w9&XZnWV1BEoBB}ld*Kv+jrgh$o`coEAewXKTzP;QR=N4n-2I3uKOECT|%aAWQZ6O{y1za)p$8#mMP9|PDi_Xstm$3e*>8ZqDtpb<k)ZuxT-abjZ<SCu!w}m8Op5zr0pV*rE*&+BF)N!mOZlTcc1vd+<C)%%d#Ot?!ON9@>O$X}fep8#GpYo&PMAUEoBk}6G?=ha)W6>XZ`Ypb%SgcD%>msac>dt$_qnn|==~6b%=Y}B<h$nZV{sgY3_4CzJsvoir>##996YG&7xq-MT8C+UsMeF(VKd8=u*5K+h>+Kkyygw;FurvK`Dh?%H+=bTDCd<%&V_iP(*Wl3|TzWAMT!}a0JZbO@Al~~a&GV}>(I4&hB&u`zB5`9Z{T}HZOZnm9WvCy0o!0jU>xtJ+r{}^o4*gLxHc%bMA>dle$7%FD?<YRwQ`C`$&Z0Ut1yrY~hSulSXR)uSl_!ZG%K=v>IK9Rd|6Zu0{BZ^QmQ++n`L|kAKV3t>4Jmgi|FQ?|7t?;Hb7|B)%76KDDfE6l_9@N%KIQM|PVF9=MZX{8nqnSEBhMjUem9c#wP<Vl-D}Lk^Q9GA@B1s48YfYH)kAQ@u=bQ+9*=y}x_JDa)oL9nzg-maRf{;v_jjfIu(yz}WE=3iUbc3l{I6co^YwH)?dwO}Dc{=*bqs|sk*|1+A>OGExanaU@g`%5E6Y(w?%D(A3F#(tpBcn&<ly{lP>j@W%`@7sXQbo2Xm}M!`K}G;(Qfv0suM7S@*m%(=OwNWorgNjr2I+c^t^bUrE^dJFv_1FZ~>p!zEO^TZkb2?><D@fke`C{mLW2dczIvq9cR<|ENc<fKWjpNl&L$=A8q4e%5T_D&)uVaI4>IKE}{JGiS&F$FQNB2o-xFWwxf>r!ENgQ<W#C-wGLdG7*FT9aT&y)4g)tP{fz#YGEPz*lQY$EETDdd6cfL5o7Sbe3Oc_^SBYm;f@{4FQ9o^OQ2mtU;8N;II<H?dQGRt5#?5GU?jr8@%5CCi8o2s(4!Bgs?`xWdqmCMuLf@m`W2#^ECberiNbkX{o)8a+$9f{oT94l+CNBx&rP#KhIv;GL-yu$YXnbu4U&MT<F;cs&2T*>=`{1U+k>E<qBH}AEz?HHF?Bga6dQYTm+6b;*`5D|$oKNqewzkB34@372;Kmh2)Nb-K<jZpx()l6ecRB|@{|Nc&tFGWmV>8SfC9pT~m=?qz^rU$?c^<u2S#+4rEo)t9o-LRPuGuBhx#jPlQ~ta?)Sp~8aA`vj)gQDOT;B5zxaPi=@;|=<ZmP|vbJutA#H&tIofc`OCr7{b_I7+~k4;K*v2{sObIDqoHs!CcZktouKlQ)Ax(#vpU%k5RGr;Np`|5U%-iNt*gmMTU#u~w1=sfme?88~-vkzw<$-01jB>OK}7qS16{X!1m7qc#5FLWvU#q6W>Sf<BUVhmZM*hg`W!e51%9_AdvH)d_bzA^izdb}Z~z8)=ETd^0~f_+Q&%{hc`#%jUdg6lQo5WWd(BlauwSgyw^)|Kp6v0uZwn!V6y_G{R$<q$rG^=tM**RhXbAIl+p9P4`aaqQz+H?bGGnSDI_EgZrpux@29^jr1`?6+|UpTe5VK83x?n#x}2H|#z17^24~9KsJ~{h0k=_JdeIWG{3e`$6p8IfNg;+K;`^57-Z2-=9Nx7uMeFUD!LZI<gn)z}|_yGl%efS$nZ}W$nY-i+#Bs7xlQrA^Zi_^XxCMFJb+jz0h;)OV}542w%i{mc7su?2Fi+;t>8A>v!yrvCn4BVlVU{`)u}^9Kxrw9$>$hbr<Ua_MP>3TaR}*gtyhBjUH|Fuw-q=-jcl)s||ZA_SPK2w`c9ZUg(?b+q3V;+KGKf_HVJ;vbW{F34dIV(|VlY5WbLAV_(R=fHj}J&|LNf?DIH;KdQ$DJvQo*$eP4Hk$oELcJ@MdvQJ~bgG2b;tb5oC-OqkE`+Xe3XRsb(pTYhx>k;-xxW9)vgwJ8kWj{ra$$A($grCGZk^Ln00jv|)3mwlsfc@tj!jIGAQ$76j@MZO9@6Vt6atJ?`bv%2q&zI^^#vyzK>t*&8?5kKS*$b^^U&X$LL-?z#SJ(@!Wq*}@9f$DsdR*7zh91{g>)F?Hj_@P&7^X*eRy+2y^q8r~7p$|{2kH^5$5hrJ_G9!IrH6sF3;U6Ji1W^H)*kGKvD&frU_V2T5Iv@|PGkSB9`EVVl|%S$dW_b?M~|U;^wh&m51Dl+`=Oj8a|my*ho>Iz>*2*}&)$o@H>(eOZ}y*wcD>BZtsDJM|MmXwe~LIby!IdQ|M{1%AN&6Lmj!yQe;ooxdo>Yf0sT;7jziW$vARkB0AYng<p'

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
