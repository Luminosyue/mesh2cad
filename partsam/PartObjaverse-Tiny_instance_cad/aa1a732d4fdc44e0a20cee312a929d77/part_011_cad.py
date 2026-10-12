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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/aa1a732d4fdc44e0a20cee312a929d77/part_011.stl', 'relative_path': 'aa1a732d4fdc44e0a20cee312a929d77/part_011.stl', 'source_sha256': 'aef60b3344636c59cacf9459be841276e33684df7c11d7e0a696ece6ee95a63e', 'input_faces': 219, 'input_vertices': 219, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18531355261802673, -0.18636180460453033, -0.1504911184310913], [-0.12038831412792206, -0.024121858179569244, 0.40194350481033325]]}
GEOMETRY_BASE85 = 'c$~eOc~}+K8OBEt71LPbuF-fU3vRJ>i5luM#2v)ou1NI)UJRhfqQ*T_6OE#wCNVBi@HV!F7#AX<cvbFP1dP_WV8ErVy=@<@l4ukg>sHN~bKWz~IZXfQALV(z=Y9FzbH6$Boo@~&6Qd&o>o!x^PX}dV+@wz$G*=WOex@{2=D9NFBqg{qyQQWrsG~Hd-1y=8@u=}p(Ua>a^OQxQ(_NVf8KGg0(0+-1L%TXc6K7}4$%spxHalaw%iu%fW@fqw&wMK`%|(9i*rWUFT^&6;b#*Lp{Et5k$rSXMqGMiTE`RBA$WU$N@^1&)aJBbpksk|Tysl=;HP2dsJ3nYbx&OyS_WbL0B47N-Lp6VaJ#Vx@;9A)g+wmrs#=G~O_SntGom);hSsa1uBRp*UmSy(5L$<*E#f6l+BUV!Gcr}S~$G%I)?6}|eIs3fs@^g0F?O9!E<!YbC?DLbWD{T4g_o}R1|FBIty{|^w&)RW4Kl!|syTi_u(tKHeK4ZtVUcD{|*X`N=D9tmq&lx+eI4=t0orUQ>%3CcsZO8Q<<1SjclKr@t^~>K**>UCGR$;vVn_FxhH}5`W$JO+MV*Y*q*l(L3T+XkYf4tXj{{H=^ciYv0^ICP-^lqMAojI55toMuAX1k8y@;WM`>Tk8{6O&7QqTP%5)UMyO#Db01zICn-XL+{d(e+hh&r}LLydmRx)2pmpZ}eIT&6j&s;Es^)blu&3MxVEGXI2B9e(rJ$T&cWrn2ujLPMDAXPX&}~UHXeWHjQ%U+KvKu-)hJ5<hK;>Yq3uECFhzT@xIDCc<i`3y7VBOXQTUKo-65;JG)&I`K(7pcJtR>n*SBe=jdD^%>SLud+6sab_!f?8nTP#k5}ow;a8qxyzX&YH+@z-y+2(EWV~KDt+ST8Lg4;@H+3r~4Nmt3XM->3cr~p?;CeuX*UJ4*PEziu*PcDsY4wiK??2f|xmrJoT{nFU<^IR(SpMJ}EPqC}z%?bpEAameXV(o5V*N8WqFCThT6?WrD<4vB*PkYr`jd0HKRK8ClXJO0&HPe-axV9$$)*0}T<%Yq^L{h0EA_3(rM~4{?pt%b)VC&=`j&IKZ_WFX`qr$o)VJ<O56Xmom>)pblXJ5lIDc4FX6;XX#KRI>zVI_)Jnvi1^#^Optj~oK+5M;;cMJ&9t(-qEPx;a^>vN|>4mxVb-2+-vb>8nRaCKp}*OteH(REPnw-M%}$Hfbr&qrOf-)qPDc;~&Fr9yoYP6*tr59j~hS!!JuB{A7!<$PVVfzxz5&c~~Fou$_2S4qP8k#ju1O86n&mSeo~V-sOMTFPaCoAUv8UwxKx`P{|1eD0Dt|2xRJeD12n@%NN-`P?OQ{`Z=5`P?OQejYHdE1kP!&d(d1%jYhc^K+M3H)-E9$4mPj=khsC=KLIG-j}qGnd7B>%v=}gTqkpWt~2vU=Q^3o^O4VWW`5~hC-Yi$md<rDm)B7~*U4P&6Zu?Mi%WedpX*F6o$Hi;RnWfS`-6KB`@1c3HFe=(D>u&r;LbbS8OMI54$kq}aeekxVZ6CtfjjQ3XXE*KX7C=L9aqyD(sP1x=OZ@HfKH6ZWF4S+YgSOM1!l5yPFkBIwtQj<?F)B}Mmayv=rQXLFg}kxSAjKbUwYe9Y{%89iS+NJS`*LC894tav45v|l$tTZ{LOQh#Fg<q=zO%>y@fg}3$wg-T#f5Z_ig=FfG~e`)_}uyTpwFqNPoX|sl+;eE#VS77yOW0!sb7Njh{8@upL*%-KBZ7n{!I6_19cs?7xF=^kw-QY+~al#L)Zlf8V&oT7T6Q!JgyqFZ-<h#?Otl_@u`)kN%zR6Y4oVfaUov*C$+eZb-2m*QT6eeNvt6v(`t6Pi6J2Ugi_(Fm(qz2UX8!<A1nLucwV{vX9QMdM2Ca?Im;{(?>)U&~eqV?E5!XvH3;cq~qP!!|<GSqV-jWdFVc*UT@3t-*B<<V~c5>o!73h^TgdscAlJ8US!LMX3#wPKTCA$b@lP_to~P5us*x*V$YAWs>qJ3LzmJ#?u-P+rT0ZL=kJS5F1;_3Ie%Zox%|GU7RUP{lS}W5YH_^(;aq-SREtaF<@ZG<m);j~F266T#qqv~bNPLddNo!T`U?A!dgTQ+&j)2}U4~z#>*73q+iUGNbz%j3E{?5Y`^CfSN374a%=L&Bv_JLoD6h2-^$A&QKP(IO3fG;n!(+#_s0p;6)w1iw);{F>gI;>J*xFax=pKdMXyGktb=6<nmo`)sBZ8G?N@ASl6{-P^AFlSVP?LK7zh0qkB6C<z;@2eJBH<#j75WGGuSo18@h$W`d;*Cr#+pGl!Kaa!MdEYlXYgN;*h%6DREOVBqJYFjXchbh5}%Sd0NoECPhvBP>ChaD-$)`Kx*I;%SVs~?(1Y;PFfJat8Q%Ebmn6<Yz3_uc3?lJ+=<ncTNn|2lCUO~mCW+Z3_CWW-4=0h1@1^5AvAD+^+-DAIVfbyh2M@Feekh4l<V!^^!zYrML1H^}2YdnQQ3X8*{|1Q^<V!&=o;wBCPr<dfA(xT!5VROxC6R=DN%+nis7EI1nu(h3MlFn*R6r}?2jCu5XcBx5)~EoQ4}So4x&*xlKM?mn0GbGItVIT{X=ovQKIU}}dKNyML^ARvBNxw|j2ala3qB8ZIt=x|4^dc8ghP|zQ*e*DP`C25XN_7PgdTz)hI<$Soe6K$HXZd%$2`8oyo_4=pcU{_aR0-gvn_rD>aqd#Ekqdp0`wC6RE(Pf&45qF+;&0tz#H@OVs3e;jq!V&!k&St&<*fOSUWd#JN#bEsS<ht-q;IrkS_<h;!u-RTr(AGlZQ1k=2Z;!!8cNj{|%-n&ms)}474HqGw{LC2Jpe~^`Z6P4Xq1bA3g{g03QS&2vy(%;p>n%L*g`vQ_yeVPr;vr{t^Bp{0ZoB_!ID7BMe^-JqB-R8GJc>DfB3ODSQcu7f8HMqAm1Y__pwEpzpx9fo}y}0^bV01#}U73;1Tx1@KKsyiKApbS`{j_@6`Pz&}S~9*L&V`S4BQn?o1EH-~QtT@2q6zBP0yd~5jUp&I=2@a>@Q!MB5N4_yi09=-!K3;rb%ACPzj`dj!{;5$M;gzpI78Tv7NXZSAAb?{x_yFx#K??mDw5~0ww@S*T8L$l#uhJO*d2L46(5a??75O@c46}$uf1?c<m%Sil&L=<!+{0e+F78(V=9G{JWj)m_>;#VXlLnpy^C(#?<?~U<>|0O;f35|k(okU*}6QJYa`{Noh(8=&UNc1Ez3i>AeFK~@W=ty`YXCLG>bR2vbt}ziB18?N)g}jDF!*|0qBA}7*#+cVI&d|~Dui`r+pb_xVk#z!^1^%~xM)34UGd3>a9~H>o6pzl<Zw@87%!71vWRS6slFc!IZt6oE#&16XRl~=L'

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
