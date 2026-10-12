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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/74c05ea2f5d64357a75e4ecafb9570f9/part_001.stl', 'relative_path': '74c05ea2f5d64357a75e4ecafb9570f9/part_001.stl', 'source_sha256': '283ad71047ebf127ca7642ca8eab2e99af982e11c1eaacbd7e10d1cd57fd22e6', 'input_faces': 136, 'input_vertices': 182, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.170677050948143, -0.09657348692417145, 0.21374784409999847], [-0.16841381788253784, -0.050568338483572006, 0.22728604078292847]]}
GEOMETRY_BASE85 = 'c$}q~3v>==8pnqa#J%DkF|H9J5pheXe4%QIL`11*)c47Ss3vI=tVS47LM6m?T`ERVgb)!?-CdnhZD~@wN48aJ_tUafv}#*h+R}aJef~4Pr)T$^J-eUtKhNJUPu}mHndg1pnMqu<S3O^aK3$Y?D{uW=+)`0YHBo$(c_~>rX-O&B!ReU`>L@KFH$PTfA3G@~E}@PxPst5PPRUNn3W!hxhNTV(2vP%5GqQ5BT<Oy@vXWCw{<LdOc8cKHvs{@e;{Uxuhx89p!vcfUJoSJ4_=qXEPhLFpwut)Jh&Roset)+*(u2FRj~<ut%vHu6+k+%m3u_qH-rG|p$D8&?#*I7vlB;>8j5|NvdQ6TVyOrmE-%4_|^>W4)|DsA6znshGGum5n)jNsLCv)*pnSU{!=a2iTLdKHeJb!ME<Vt2RKMy5eACW&_(~*z!L8|16t1&;WyMHT}KM(lfLv~yp5+qk1{GD<4?fr-4`0Z*L*CJm#B*(dVnsIgA>N5E~<%b#9uW1M6&+~UM?iieXK#sSwkdOb(>{2;S_Cm>(sTU~U=Y*^WrQ&|ICwCr>l-&8}>x>(T2V^}cV`~|A*Xb|0e(DtCx=W{e7<z=~dk0AFoLa)TqjH_B2jxN`<61&{$@S=5#+3%kWIZ_EP2>5`H<MidVlw~U#xGNyB#z?a98o0KYr}pu&K#<rn6CV|yuOq5V9aUG^OIbXJFh=v=UHobL)L>a?Ka~|)kMjiA75hJSyd_P#JKl9zg{g1Wt}+Ft9ZUqQby}#H_z`lPu7WZ`g%T}l%=vx+>11xZ%m~+`5|3$E%rPeZ{Qnm(z>`^?a7tmc**rSZpPJxn~&4F_<(Wk^QR=&>ivP|FDa^`b+L!%e;Hmy=V3GB#)ZYQ9vtNwpHD=P<VH~r<BpzLm9#FV@%+dxk{gRA@cceAWj$!&;f(8RTS@M2)0fXDFG1Fc*1HWK=URQq-3@$retzr`S}%9md3JpDqpSz_j_ZtTe{o2zAN`2)`Ils!sB2F#uEeDtqV-bB^Ow9U>%`rwgmHI5oU9Y~umZ-7p8I8;s2y_o_`eL0bz;=cklcB%hVnyKQJtV~SX?i7k=2QvKS-1H;7ogmamS_U)K9R#*nDLc>l+q#2gS2GvGZ5Yl=YzfV*&r((9zUqu)kPbxthTGhQ+m4!daczJZv1*Np62W&L@4S&tQMC^M^#qda(M2o&TB2>cryesxaD*>fK`JSqpAO`w{jR`?#+3pgx1X@pzsM%RTGFK0jv$Qk@j-V%*u}o~#pVf3f-O4pb-T8}|4|K4o=ckDpVol-5h4<ofLGG>%_yx(_L7UgOF2QM+h=$^50-lPej1R43>^7I$pkNc)THGsd-dno*r-XL<hiSLwPxIL`Cm^P)OI|FO7nXCdt`H#hM4wEw5PzE=OSk84B*UHAM<p6`E)`UCopJ)hCZw7+D>Fs^4_q3e$RV{!ME$&#y$1Nk_o&&%s;^&flwCDF9M{9K>s7q66k!|Fd4SHH-m{bj>d#<hXzvL3AdW9P4M(*CmSB+rkWBJ08GKlXW8H<tF7PFsl|+(gH9c^~zSV{L0ZxfZ;Q_K}$Hsy(?gteEzT;eTRWS)NbVF{F%f<6;i=|Myogu3t%$*ULFQnQ=$IM7myaQJfE)K>L1_KOetfB=zS{AMoR<d_kU1_qmT5*H2E8=S`nc!MKqWLF;AW8tS(bH_~w}36bZ==<8j>`10=TzTM*b#Wu7qj-O=Q(Weo+54U;0NAf(Vj`@rm`QOrgGVZHwUT~f2@N5Vl=h7#1-;4WXd!AD_$a-_c-(bgOBrPhV^>vybZ=)nxKaR_~<i<B^X#Afx(*5e~CN-YiaE+jTa#ms79kYVY&(a&!o?K5IOwTpw8+Lwto;+{voHLB8Cj#kw#-CtZ+mk{4r0Gt^jmCa-e}cYYac5~VJ=Z+S<M}OGQlGi}664Cl$<$9aCGc^Qyr}=6Z`ku0KZdSX!63#Rv+h$rN$$<_pBYa3NarW`_x}DS>l^ksd;8J#ZE=TP7q#PC^j!1x=bTT8mi4dhJIA=vV>dn5pl{goc^E?dWXoR0o#$3iKbg0U=fCbN*NYmul<H^WYTTda%6f2H>jhj(n8xbF<_$CXIs#V?j;DR+tt*VH&&}ZL%lh6&QLIkvah%Wcb!X3Wu;k8>n>eo+Q_0q&^}Uk=S)EwiQGXbF{(U@8f4V=Zj^+72p%rZXf*WNmDm?4N=84_d^RGRQ;ze~esR7S-wJT@q-8wFxZ&{sK+&!x`d;Yb@Ib192MEmR8JiqCWtUuV}pE$|t#LjPfZNEIv=JRhHdz&+5^ZEO3Z}X8<bRET4Np*R=$}yq&vEsjfm6JB$zk8JvHt7F-m2*tYp+smZWcrba3*kq?2O(y{2f?=%$`C3L@`X&_2XQ-mANUc7mGC3r6NHWmy(TmTGJO<cE_@VxZ^U%?-teu2UKCm`^aN!3K*VkEf$$E*3U~+nvx@l`uP9rECPSu=M0^=O622GW9Qa=F=3BcLgq8`lfJ`5NxCK4{emG(|{BZb5LWhMm3q1pw{z=3I@K3_`M4S!Z6TZ1nn$Rmk%^=hFK>Qti5BOn-hv0|7PZTN>+9VVYnSLnZZ{df+cSoEB-yOcG&`hDFiuwAJWcqH18{xabM<5=AkAR;bbU<i>P#k3XaK!oW;qYA%Q{lV9Hx^0}$`|s1Oy31@J$x7VA&8~$L*T~??H5`n6bqStFycJ;!SE_#GQ0}kNGM5YiBLnx^qmpc!gq!rgt!lW5PXc#UZG;4aggZ;BF=>$2=9+L1KuCLfsji`6Y_>k-wAOId?)w;h;P6TfR7g1BeYs*EM)pH#2olAct1oZydQjhq3J@4h3Y}3?}%6g-x0n);%@l<@MDB_2^9+c1~PppVm5pzd<Vqm;XA;42~87PBvcnNeS5@J@a^IIA-)dZ4}P@JPN7$Yo`y^xf|vy#0^bfX5xyOK9iiuh@|4FP)3-%j3Evhz7*U50h94!gLuiH2Q;_NVBEAIQ7ru>9Ty&kfzFz<7PaTgxnmI}KhmT+XCf`;)fAb?Tmc7ZwMc0>GYhCfroWxh=Sy283y)O|_'

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
