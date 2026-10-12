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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/404f12ba60f444bca620c4405ef50bab/part_008.stl', 'relative_path': '404f12ba60f444bca620c4405ef50bab/part_008.stl', 'source_sha256': 'b970524fcfc462b2e9f553192d913f204a254123d770c8d6124f3b234d309f58', 'input_faces': 224, 'input_vertices': 168, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.40369024872779846, 0.2484341263771057, 0.13074198365211487], [-0.17176246643066406, 0.4247070550918579, 0.2746807038784027]]}
GEOMETRY_BASE85 = 'c$}q~2~-u=8OH~3LtFv1Mui71prYcwA&jCVLPT63VxvA}kxfBRRE+rIQX|I1-NqVtbwlk*Tx+z6aWrn#9`IQ!QCsu0v93)#^_bS0#Lm6{|B!jp^qiiSbME<m|3BaR=DYXK%$tFv1fP0=3VuSA-==&LtF}-SF`6iWN=atXoSgK`;-0e#7kDWxq%VGqxIQs?Oj4?sQlcyj%g8KFFA5uC3yaDc6c%9%%PJ_EQ<OGqT0v1prtss^@{2Qdzc@RsFjLpzy$1}6u=VX4VOwPTAAcI_EjXKBy>>#6j>fw$#fW$<vO31(t4hFSq1{`3TxMU1@VX|nntT1E+1EnyuM4eR*ndX;{@L%5-=USPW9!mD)^U_wLjLF_^0>;*>}s>`i1{myw<Opz|4|otT&-f;Ne}<_T6tXc#e5t$yBhw|uTkf#5E<PO@YV1(vLEN>M$)&{o=1Mf-;n>Xqm1^wr=@Qj)E508Z;XB}p1`~wO_BX;=@r#xU%Pc4b*B&U$k*Z%WdDjg|D@Sh)g!WhhZ-yU*Cx{M`jmA#qt4^w(zlPfi23Y~l2O}oRQk@3tC8P68uPgK5&G=k4*i!jk-l1e5cP-r1NmdSV7?djq0c9mq4%JUed=z`w>{SFQd89b^A6-MjKVrp*HoK*$LuQPwVB|V|C@a5<D8)<J^cN(*vCJ#l<Q#oW;^^NwU}=*`&kU%w*5K$Z1k^;q#v;t^NL7D%&g!(eu(_g6s*INO_<k|L&)>;^tJgxa=!M;W;kx@M&v*HBj(d`7}o#hTIsuQeUCbS$9^fbtFT{tkHIgWh|k?xhC24!=%?XO<d0a2ec2t1{d$b!YKI-@ziBY8m&E7QX5Z~y&ht3iBj3@r9P9kF`AM^{20z6*r~Ku#Jg<@#qn|r(qrd80)VWp$|Ez}k_r`hn+5<1#AMSU;JUT9f|IS*}Ny>wtGY9^;&8U-(`p){rn3wx5);D|*e6K?Enat}bE)nPd*aFO})P{XIh4oRV=AnL4B|h(+&3&eSydLt0^SYjAhd&PY8QYqESpO*a?r(73+J|MJ{+VgGzP_vB`iw^X857Z`PeYvlSAuHHzVd7~^0$<F=J(x(eVO%0^YFViy&;cRb4u=uS~>yqopu0qhD}4AX!_oBq367T-@h1(K0|RldnJ6EKYYh#Tu1hbk%)KVF<;x8$g?d(yf_N$)97Q=k55JY!?Bpxrz@eK%tM_ohakUlJw89G7;)!7od4TTqfX^`_zxrD=T&e%GjU$UbU~kI_n^LC7WO3|6n@+TxxS8=!8K-IX=_K_ODjC`)qunJo~n0Q^T_uNmg}r#?3U~7wuiuvPe+~An4jTmr;zVhx=-dS&4ZDD4Ck4B5%LXRZ5M?4e>x`fZK>^$pInIimFUy(Rj-$jKk}T+*E+zr1^gO)1W!eNX=|+8M+;Er;!+P^`&9tWAD>#BKSeE2|AS?`9?M)F{y;y>>%={oZ$IjbK3A_n{W9(^eMf&U^f~)E>c8rZI^S+ZABziIW?#F{`^@rY@_z2f`RC`d&NA$;Z7=rM@YM_Vk)IGE^WDi0rLVNUg8kk(y2k8l3hwW2?=>#7@92Jl&j}|rv#*A9!}`3~jQ+oPAbnfvB&^Ri+_wy0JH-4+l~|u6_oeUrdJ2v=7x{*-eHo7Rd9(-lH}0Z;Z_Lx)?Om7IS0{EtzV}g??_7BYb*^I_-GQrIX5aBv2br%Fo=5-jx25ln!*%N%vD{_$wf6(j|BdUYUvm@vJi__szPZR{_8nJ!QUAbK_+Dsx1HNq|^2gwQWBA&c@8o_d_q_4k6<&*eW^Tj&-o^dj@HO{iJm<Jt%Y5gOgQ&m%cXD6V_G4?zzLJRV8~dm0TxMUrc?#Ec*e9BYf29Z3bHzHW&&%-byC(8EW`oP@JF<FWzPH}PeZY_T8IzG8h<w9W3L}uee+RDXjR!EVlIh4hkMp6<{~`?ioH>a4xA$XxO7fAnX|>DjJ097vUo$_$eISy4<N3(jg?%%8^?DoB_rHqy#_mI(wYc8hogFT-?|9e*`JoR`KlwxC_vQM|!}V_X>LCUFZ1^7avp+!pRrsEDKf!(5@Rh13I3JGs<9x`CJ^y3-YxvgvHGJ#-*7=tGwSVS1C+k@54~B2OKN!CC{$Tjl`-6RS2J$W6JBDxl-Z6aZ_fB2D<$K3j`Qoh1w>&=>zV-Q`F5mL}Q0H5oADs28q;Gw0G<@rGqv2bh8x7z3+~}^FDt+tozu{Y-|LgKC&;ND4<@w+7c{tX=`kqDq-`=wf-};_K-};`V7Bxh^<vrB!t?!|A`Ih(4I^Xghsw91T2G_6W`?cX)->(hd`hIQr9`Dyl9)Eq9uyj^0#ZO0l_$q-)R+{Ng5Aqj^QWt;xPY*f${;NMd^y$;@|NYZLqTWNAK3)~4q(0KAlgNqWOzH{bB=QVu!O7Gj=8#__CzJE2Q^~K9XHx%^oJuaB7CjZ~V;XrbbvikXJdZk)oK9XqJ%gM{UPzroo<Uwjokz|gFQ%SJ&Lh7`T|k~mUP|q&4=;T*AlIYzBm0sYQ@14hk(*GrBDW+5Qg<M?BDbOLNbW!mq3%KMNbW-2kKBXYhuWXLHzWH}2ax^Ae$=hW0pym{?a8glt*8ZuQirl%!JWyW<c`#WBdH_Vui*aVNOC{wAokvt>`xs`4k8Co3${_)*stJDWE;6Xbp*K+Ih0y(Z|dIcTkt?~Z*nAc40#~AKXrHZ9!?IT?n&-W4yG2|i@F#472KEHi`<EN0J$$Yf;x&kfZUsUI5~<uka{F}I5~!T7<(T~?oKT@nmU?&3s%X|<X+Sx$SS!nbu4)Vc>wh&ax6KDI*vSwJe+zQIgUJ%I)S~vLLNpvhMYi-rXEWkLsqHBlgE-rP){U}C&y9?PN7a=zk(-`Q^;}DlgX3F<EZWIeF`~&dOF!o9z!iSgF1u#3eF;DkjGOC&Zf?0--2_=+2j=Jd~z;%67?){K6x_r9QHn&Y^N4nLS4eX1<xm!kTa+Smr|FqZ^3VnOUc>PW#l)=xzrAF89ASN3E4rOMg6)y3fXfZ=OMUUA3xK_D#jJ$3Vm$RM<wGgOuUI&#LXsNM=j!d6Td?(;=3j;r!MC)1#jcAw=-6fcj{w@KB^dZk$3SkRgBxoztqS3`fxICHSv4YBL3XO8>vOyVB)pZBCav<YHAVRChz32cQ881@d}<DMl((&uhhqKeZ0lEjNC{c;=e-;8JnB99kqxrnYbIZh+R!Qlv>0gCXT0$XD@=q{)_XVn6Zc~e#G;FH=_@^sXl(9;JZx3wk8gv7BSq!gQ!IuY~q)xMSR7?uTzUSg*=UYO=T=1*Jn=+7@LuOxTfBW4arFfUfzK||LI?MKm0hvq&@zTXZ@t-W4HN}WqPf;hw!9?`l28G;NJ2gJSKKd`4{^ST|f'

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
