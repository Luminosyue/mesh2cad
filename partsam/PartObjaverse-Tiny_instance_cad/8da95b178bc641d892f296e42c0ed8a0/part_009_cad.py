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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_009.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_009.stl', 'source_sha256': 'ef8a2f36ef3fcc290fc45be71ab08e81e665fd1820599a2d02c4d4b8a1fe75e7', 'input_faces': 288, 'input_vertices': 198, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3688294291496277, -0.24289409816265106, -0.24497848749160767], [0.4634816348552704, -0.157537579536438, -0.1264147162437439]]}
GEOMETRY_BASE85 = 'c$}r03s4kC8pm73Bzl6VsQ6wYiXt(Jk3f7a#;62A)TkkxxG1Qorw9f`h>j*IMhv2Y0zMWIg@|t>;&a$tA}**gm&A9%DVMV@iC)Ueov~uwO;7)4=pNRpt2?T``u+IZ^z?Lp!|qZ>hBb5ZBJ9hDT)Td(g=afLXtg3<Bqcs+X~OLI<o=5iQ=1S^HK$)1w?<42kBn+UQb?L#TzvBEB)>OJe#7Sk`30E#<}6NHniRWe=HjHdc$$xmU6>rN<jM156XTWd`wR>Y3NQ`o8({j-^gn*JRF)wBkbh&8LMgA#d6BMZY4kOfqh&R>9@<vpDkla0>UascIi$-?nw#Uk7shM3RR8^De!L~@gPX4A*K*_h*8TZ6U9HplYt3z%Tl_kz-%IxTFZi5Xa$Hr%Z(dW)=cd+ouBhXC{^hbTJ~r%%t9dNxUDTXR`sxy&OS5un)$z*;#QD?G)tuaQI{924R?F@;+ef&rx$IYVzjHg)2=i<AJG`5aTeN)RL}4Dw&dV%MnIz=ahjUr(K1R&Hb7#5#E8=xqJz?i%Sf}h*&vNgF!u?8DMzh>_zkltk=483JKk}G+>h~mXgpiZkBK3R8u+QXK1{*(et}wqjxLzGce8qE=dc?3iZn(J5tDmXoDxn|9*l~AV^^cYt`$x--{iBaZP9pwp7sea<K_9Q>xkMN*PkqkDnU31{+}I~tZtN3%yp|6=EX-p(cYPi$548*9jpwV+ujPjI8_%mzJ|s>UZ#+k1E*bXIc)pGDUYi`kJTEwREhi7gR|)$+=se3;m0xm|OD)=ped1HXzIU+xF{LEB>?<ud_LY_!`$`{g=qr7^p|AAuhQ88rV_#{xv9GjT>nkas;EJnU>o<KKL%$hwDZ0PR=f*zN=Qs4Bo*Vj5pWo1j`aT%?uu+aa)b}Shoc;d!o40ts$VuT*Vg1IwHRh7xyo`O@C`aGw^BDTpm}`BjuiwzO#$4-LeIH)Xw{=}jEDtFb&P7Hp1@;!s#gtOUp0`WO#J<(?vMIuSk%9gW{<`GkYO&wereATDlLy1p^+>xv68q}RMw_dg+=x`qtL~RAVxE<yjyK=kCeHtZFPr~*j<}wlL)ktY+aX>zA)Z~gAYYuvCtMvbzrIhr?w+&i_&VQWasG$yHGE!I-I|R*{-roRW;W~d)lKa}o;jZ7|8{5n)_K3{=M=fVp5W~^J|~yib)|2gI{Dm+_XDKk6CpS6nZfd(p9=GsGi3H0{cEzY9&6EN_8gs9tmc;12iQ8DQEdHzb|;_9+I=OTXX|n+!FV?||Cu^FpUdTs*>iXQiJHs5A;)#4Z=#%hE@doW<12DmKRzyH`N}pd&kAPGSN&(=e(nva;d8wo9wyrOoJ@#d`_uWZlh5TamP<>%6~;@MPuO+Sui5$BTI$a7eQyZsk-u)i^1=vlowx6>=jz<oYHqo8P+VuVw~f!WdC2wjYCb3HYuWSuUHdQiTv}Q#{N8AkkG-W*wjUDr&6daBZ@hX=?Ek!VLawj#&TBS4Co2ZA{hZfH7%!)?T=FOo$CudI{;Vmq3)fw8mEG6*?p4A(y;lh9H*IpiC#+}Ps!H{K*Ld6$?yK`a_4T%HXnQfw@Dy@=o}Y>;`CRVslsy+Wx7YBw6}hylt4)|6uNTs}BqyI+wAYb}5IdifjuGs>k}g-f%-w!;@VP1IA65K5NI%aM)=z57)ZeS}eT#U%*(UaTd*K2x4<8}q`abx6D)TvczJ%>VwOq^R^6$tGwyYH9@rq~b3$@e;^B^aq5^TaeId1BGN%(xE<yPdR?Q(}Ok7tJPI%Ubu5%(c<k-8r1x?C}T5X#OsZM(P+eP^)yTCzjPr9a21xw-jXwodJJHveulpIcX+tK!$wD93qOo*Cx3bHl;sB-vXyckAOKww{V$)>lC}PCmER4`F?kn#Jzpb}{QWj3*;|*!jFJ-k;5rHbBkI*Y>mhaeKhd@vEvDKG#1FKCfi2zm5ZJ9{)1-T<`X%<#UpFi#-?FHNto~x)+=0rzo2+&vg@9XXZYqFdn(|yRV(k&9%R={e1LewadKVo<qo^wg~59ttb)CclzjBA%9fQ<}G?u$>(+X->^LVpR9ilm%8j9E!Ur;Zb_9c^O%J~ZVIes`*Z)78a^k;rTsUA@uXi<wm*1X*77=kmXm2O*@f$7UuVx(zvtC1^Kn-l!aRfKHSAlY@Yl32Cm%UQJQP)`1@R(tV!1!1ssBKTPS<}*OBnoL{V6Rl=>PsxT2EySy_6b`qCOJr4Ic>~g`)lz*cbj5d@R@xJ{CS6d<{Mx{toy${2h1%I1nBIj|2z7BjJ<5A@IrYcfmK{@4}~oLGY>YDd14}6!;`?FnkhxA{Ypt2oERp@M${`(h__X-V*Ks`ocZno}eGx6W#{w18)Owuaq|!0QP}X`olw&>aWx|FaSOd{x;|je;Ym;>;oSSH-mm~GkgT-3-`r+jzCc#2KvB<!QWIW7&L)Ca3Acc2}S)CrTzf60$ada!QH`@aCdlX&;#BY-VXGHw}ZC@+rZnxy}<TxFL(#;Y&xK*cT}nq*cJ4Kd*ckcg8kuL;RC=>IAu7TG7vrh-W?nar|bcz>;k9k4DSx_26lpX!aBNv1K>@SawF`k3D``j=HSa9ffI~>8Abgir4p2~D78$f6H1*`>WorFN@Xc^9^X@DgIVxwcm}u*o&jHuqP_}6Jrm4=XW@F8DC&E`^YFd!3n=O`w>}v>3qOndp?+McV@lE2j&ooIcntn2cmzBKKLS4r9)}-=p9C+$DJ$V8;io`5{1p5&SOuqaz)!==K^wdr{y8YaW!x|I!{8zC1pE+uD|iNe24}ey%z$r&Z%`^7Oan9EY48=`a`>OX`QUQ+eE2MI6?_&v2F!$0?uEy|x1*@%gBRczuow9#>N`=?cY`+gZnzb6z#TXbD~fs{XonZV_kfk~J@8%NMffgw0g8GaY3R#56!je_>ibaCi@^$bF?<tg=;KW&>K~)1uSHSc3?6}Rh93lv!YNO}55mj9Q*g@t@G`hor#PO5Qy$>PP%i;b!zs(*l%K&%;H6+Wobq$H_6(GQhv22~9B?Z<2mT4T0j~8u_0`}?Fde=U{vnEb3YZ2@fq#Iao{XZN1g?N5!55>bFCq=k)gl!2c_`|0QPk&v^Wk&gaZ1fJa6X)J7MwB$J`+9zMSTpo9Zs1K9|NBN?u1W(PX~9yr^BN_D?AGRK3E8UAO0S=2mT&>8n_EiSpc5~4+HbyVek-e2RsBG4eo<e7Q-nw!6`q6N5f}>YvGj3;FK2lY<Mh~0FMU$h@u`3Ccqbf3&8~VQl*wCl?o=p6Y=k<U;;b=Yf42?Uk|Q@Q*MT@hi?H7!YRw(+V6xdDC*n568JWFE?5eu%z;yW0?&nSBn{8!M(`u}M)(@SK08Q+eYS`UYtq!K*^B-wM#Gn+zOmx}V}|i3#gCo*Pev$n=^sKP!<y6gTFRTYrs^SVpzo^5e*he3G<*'

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
