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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/abdad363791d456786cdb511082d9d63/part_000.stl', 'relative_path': 'abdad363791d456786cdb511082d9d63/part_000.stl', 'source_sha256': '440fbe767cf69f77aa871b439ee989191d00712a728694bb264f4e46455d67cb', 'input_faces': 280, 'input_vertices': 169, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-3.354503631591797, 5.107017993927002, -2.910902738571167], [2.7867114543914795, 9.869258880615234, 3.121755361557007]]}
GEOMETRY_BASE85 = 'c$}q~32;@_8OLuz5_Z`hdjj`CA%U_Z0U}AREDB{Yre;9|ZpcE|Lqgbtk040^gD5n}CNDw2cE&EYwHCGa+0lwPMHy+!U@H${0u^Kt7r@f?eCPhp^W2lunNIs=zWM*||9oe;-#PcbEE!Xq#rO>O<2N!(Uu(#1Zx|G944<*Guyn<O{KB#!OH0;78SS}GAE7&EWKGYQ8D*?A)+H7cmgScwrkIK2ipC@kG82oIm98kwTRL}HX+a_R59KW`D`b9Iab8IwyG|OOJa&*da=;+7!u%gUt!NE#e{L0G5*U@4U@^5mOsY?peB<0k?gxt3opdz5b-DT@IX^ske=qJ2C=EM0f8y>>J^AIY^yYr~_4AI#w|Dq1%K7%A1*UHNh_8%qRoygo>lePdeq&Zkzg&mF=?3nH{&t?<uU&NUtfTP*dxxBp^TSndnYw)8NAh>Hch~>N6Y-vT;hUXe-SMpnA2=G{I(_9MIX_r;$jv`<{1ZpxTUA@m%lTHTI=(OVmfVYu&Tpt_l=CC|@|%H;j?Vw^k;`&^sARsW8$aSJ;|G2cHg)S4ev|cI9qQNBNBC-e%y!c~`)jRww*~hvmB;IR<MgYppY-EXj>fm2xb-JF-zu5!);T!oyrc7vExaJ-hn_8W>s)!F(b4()uV0q)BX$1!smqSekNM^^&-!0pW$MO{_{#X9H~(qs)*tbe^@m&M_;vLWev|rCuJYFZ*xfk3p4R{Bsq?MLQ`|ZS0;e6F|Em*c<a|4&lUwH*mo7LO-!5*`=ovqLvRmhH@@J0558Rz~Rn8Z64!l=$)zSH%zI;v256$0h>c$toI)3m>l3%xe;j8NpovQWg>J#ym`dBw!@zmdVxQhE`#})2+thT=+Km6Bov3#6G<9o_}2!6O_Rv&NvZ)4?gteaDAIU3*I)A}2}o_mA2Zw#&R?mPUz8y|DuK9lnoN9VU`_}G&l<GAPHUQMH;^Sk}@vYa10(!<@~)I*;;IzRXLbva+`Z|HRI8;-`e@<!bBtf$XmQ#XFZSH=(A%Jgg3FMMVFf!%NWwe=CcQXgy1HP5~WmwXi?@2{QnkFR83?62@`CExm4$`_90i+tgSYICA_J@<U;^PC^}=6(5nW#2v-7wtJe)--;t`nGRy45`sr5G9XqZBD=GXncEc6kosa#k^|1@I}5=G%8BI-@vgfey#e}_T*-k<VT(hB|lOhk-y~HJwAWlS+_ppe$B5{-zt6G@Z`5m=&Q|#FY-e#W#1*=tXtx(fB2Kz<Oj$9(yh;iA^ckS;pn$qzyFPIDc{`n^Dp`LYP&Z*`xV}m#(l9b!OX7BLmJ=if4c?m*JJA~d7MzYZTy_5zWv&?ulauUOyj<&b9n9r_kE%IBj0XrNq*$q_I)8Pr1N*5<Lfc%Gx+>w?j?S|p|7j?J~i=A6gTta<D4|f7e4as_qWx`^|!CRe#g=Hfx3!&d|ytuzNmv$`Fr<172h8Cl>7dKA34uQ>-lq{`u4g?{=9_VgOB?XzNz?PoZxX~o!EEbN9sSbBrc@!?ZeA>orNE%|BW|1`4PYW4Nty$-U5HXdc?V^p2E+Y>W3e{!^a6NKg-|8>i#zIv0o8i*~ie8cfUwCnx4ZZKF*<arPHl+qv?4L79Qum`n;&VcwWK<DPPLtMC$O1;@kZBQ=Zenn(&=;&3=VbSM&3wzE6xa_{w|3O!MX&sqT9wG~=%OUQynMsxRJe!dKsWfs+HG`28#IZPgd=Vd1Oq=kTlVyT0;$q59(c!de+0EsrniBYgGyD4caHM!qlcJt%zj`_aty=10CC-`NoBStoujQvJx!Men>AD~})feuS_7JZ2A_8Yhp#{S41vCH8&p{~*|w-8zewhR-O<ll~+@CVhnJ|0J>C{{QMv5+lY8`+xr=F^jEX0*hQ0v!MC#=>Eoo$D=J5{5Y6&F8bt3Ogf)M4U0`IYQdyC;62G=D|jo~YQej}q|c*It;D1+uy~2ZQ5J{5q%Xod$YL*eFWL@)>%gSD(dUrFqz7n!SyZxk8cezcUNwtnz|WxVY48E?0gSZ;*MfIr?m`x`S>%98^We>7@gVp?wB>*;u!a4}!?oZE*v~2!>sf3ElRgV?1B-3oZD`vL{t=jTKl*H!m^6qzILx8}Ou7di?Z*-D5wtacgWw>>+JkGs`!P4||2`J=VAAK|9mL-5gVrOCV(xnAVf3k&_%PN>XK*cx=fI>};caBG6TA~`&w&qu4`TkUxE8z*>$R|7SzywM@MwSMfajns3tR*yorgYI5|ch*xX&LwkJ(^S8=i&S@z89<MD)#u7NAeI#H7Vo;{q0oz>BcH1*p$j@LIGj0zU~RU5P%6BwmSoqcdO5Vj-AxHoO3fHQ+U9TL|6=-iY~U<67_nte2jFB`lVMN%P>*^IHk7MB8$3035*ldAJr_j`h+zZWW6%Flj!#3Kma+pF&$1xEfrI`SWotcnQ`^d%Bp#GBD{}c=SB41Fu8dGH?aB0`t$swcu4)FYWPa7A0U(8y>wM)`Qohtpr>JuEP8_t_3f~dg**EWw8QGS^$r}4>p50qiqFv19$`GFTl0n)mSf`Av#N?VA6T;=<IC*Z$eusxCUH<`RCzU@KUU|FN=OGMuAC3!b@Z^8ax_pqrlU^q(4BPQ4*6*W-*<`7#7K3(y8#0So8<?M_V%ZdtlQ0(I;7A(kTey5n$4X;Zff{;67*@0XD&;!_a4h#H5p0JjQ~4E=mKF{t(_!7DK>8(3S=s1STDaK4}t@K8hN2W6=fN1@}*09E%um4BEPY+k#1b=+i}FAMT$%^xvV5VA5!KCTh_h+7ZzQeLF&Z=+jYRALfo_(UnDKFljS*bbk7Q`=PBfxG$Kr6Z&+Pn6wS*NA>IlCXI(j_3sVtjkaFk)?m_B=+jGL(stMb+KUu0=_BxHzJcI@XiEVnfl0@pPm08((=kU27Cpc{Fn<f|Z#Qr^wDkZdfs-&_Jgx-~#QMI^VgQToVA7uO5>fjB(C&z?*sJc)=IGO1V$%CC2K65cCLIlr=6eAA0NTcaGr*)X&}Xc~q|>nfeij|T9kBQ0nTC5d{m>2w{I`=ceWK8(gT$n5Fb4G>4kjH2kLDW*9*MT$;K^XphtOxZ#H5o@gTX9P!Kt`^^5}e~gVWKL3VsYsnu$KC5@(`zbbjePCxA&?!W)XQdqWctgRzzbXixM>keHPAH)Cp4w6EEJ`j_)}p8yrq^ABjXr}x)Fxn~_4EAmTX#?)9k_v|GS?fyVQPo?p1lzYe2'

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
