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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/42e5ff17de214f0d8aabd509f090a46c/part_001.stl', 'relative_path': '42e5ff17de214f0d8aabd509f090a46c/part_001.stl', 'source_sha256': '62154a0904d6c03d956c7beb9cdc923fde323ac89c4318b1877f98fe7fcf171c', 'input_faces': 288, 'input_vertices': 158, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.142581969499588, 0.14563845098018646, -0.4699053168296814], [0.14258256554603577, 0.4999992847442627, 0.1368284374475479]]}
GEOMETRY_BASE85 = 'c$}q~2~ZT-9mX5v79=9Ns6ks10i*6BcptO}sDL`^dV#wP3W$p*;DL&^cz~=TE{Z4;XEmD5YI*E>MupLs7)>;B%`PB9rc$XgTNSg(9?6zwL+1Z~U(fV3ld4oQRbPF-{(QWC{eQ1tcbBG=PF|ss`1O-ce)TBW6f8-kKq*vOpPgU0d}(&U&{b=SJf!b&PCw17X3m>oTI3<Emo`UbWfv^Xj~XLKjmsGoHCT?yS)E^)pSdbyb$(Vh<w=<<3bO5aL2l-nZ2NI^?C?>8<+zx^a<TkB{sQbnP-Nv!1Gzc=NrK(ws<x*Mx?KIH<x|SdpX|I&ZhM)2n{r!y)^GWE&na%N<?0uK+>iO&+@I>(s~%pT@$ty87JYkL^_eDapYX$L<kqaYoXbx<pYicN(=#5AZI0+?;fof^Em2Kwb9uyl?q6w~&AIjEInh3KPOH1z_Gl)zw@x>S{EHc!n-_fC>Moak{vzsgbEe22JbB9f<o~VJU2gv1Jh!(-riyX;cKrqSQ+nBb9@XBY&*g$t?niy$)8;PM>SN4pLyn4h>6R?U^Tgxl-2VO0W__+S-)+{9-<WITw|Ptx{p<<4%k52J&)nr|`<!Ndu3SoP*4NXRYxOi2CW-Y>kn%IirKGDZ?sDaqA2;iB^G`l+($B9k*XGxpmniy~`lCDg`aAM*zu{c!H@?MPuD(9hrM=Rvx=CMuNBezZJ!|XJm}~3Pys+#R&%1Q>SDdG>eX7rG7k2RdW&UXNjRajTEBm+~H7C`jAIqolygt=k53lmLvg1TQ-%5PnS(4JM{O^CddxOs#d0X7?+poCf@~;){UkUqXgSe0PUg!CZ{_YcQUsNgTT$6f@>rn3fnDdpnF1dQ|>)-L;%h$zylxVri?XB0jy~W4>c7iUq#7^UNs{}0&=iOL%ne$5*?(z7-riuC>w{`b;$n9>m-O#s}b1KF94_eovZ*O@uvX%RJK8WjM@ji2j+ed7D#OL*%!sFC(MY+LsGnciB>ylzF@_DV{JTI1tWFEgGf8&o_f2HzqJ)dXh;tP~ZIpJa-@OkxFgFa9HgV<-%*OrU^Le6u(HB0PEJG(VD=<|XYG5*rbQeLNj_dCb^g`Va0qpDFnPA!+uMu_zm^iqufql^zZe^}1@s%(yF)aTNjS#8`;-_tvJTzQqJxejxC^S&W_XzO3(>ZQB~+^*NuoBH;)9xY-WTKBi;+e>FlME~K|E9@tFpXBzzg?wGs%VT&vj@)bX@3}5{n@jlL<)9Nh{$+!BzGT03w_Wo3Kl61dbz8Xp(m$$?bAQ)b?{j`JRMbby*L4>A&%{99SCyi_R&l*Q_v3MzPbN0%bG7ZE7|+%4?L7YW#lf8S4HN6_)JrkH$jzaxVt$tu^ZZ)d+p8u}yCEZapOl{u5c@xJwQM|(({{W|t3H?amvU|{$-AlVN6skZ^)J`#xUJ8P_o?H&hJC=%&zEUj2kVQFHhp_b%nYul`n0CSWjuGL@_Z@98TBsbt^Zog@8w#aUu(nASTRpyIhS*%b3L_O`mSBnGvbuW{=DEIU*|4wZZAz1_1AJ`(*x1|UW}-JpTox!+{~{dH_Wd!KIlY(yY-{xhV`Q+&pyfH_+TYpuX!HUCvw}dVPZV*R`L3jw^g1_aC5(Cx$%C{a^wA?<;MHPHhIT~+<*TPG0x-BJRU8VUz;l0C)D%(D+TzU<74CgfZVu0DF5npp2s&kjmIP14QbTpN>X33|NOX!_a9}$n-_RoO(9}`OBCzhkw0t{>wm)@UjIr!%tg)(`==u}?4Oq4GnaUL#{C(2hyA&v@G}3M@p*x~!}9`phv$XXkMVgi%ffDaerb7!=hul;exL2|d_-=1KAJuE@%y#${<VC0m&a>-UTeAWd9ALFyT#XIeC{tP<J|bZq2<Q+4J|jmZ)mykeM3FBna{6m59al$z5f_<?fpl~t*-{SyyvUdVsRZ2k6qr|jk)$-r?#k~pR_eD@9oB1d(TwccZz<#`o`tG-I#0dy=ufB&TX};T;9Wtxnul>Tzd~!O%<XJQ=YrLZyR&RdGii%F14<3d4D$Mj_cZeQ1lZT*z8g_L++?sO|`h*D-T`XSB<%2zTQ79&O7d!%X_c2J)Q3Z<M*JJ8@~q~x#4@z(U0MKP>EFd{ky~WDRP(ZQ<KZr_#yv|y`(O7w9DWAHJ+2H`xNJYkR*q@{}f*y|6hHI4;%G=e~OQ>k6|X27a~?5;v|ST6(UZ9h!;b|OCaK0h<F8j6?n8=W9^y&PXLoAg2_|B<cq-M>0t6qF!?etc^;U2C3p<3b2Ky#=O2e_9t%&<aT1Obz=`lwa3VMbo(4_<FM=-yF9N5-mw?m3nebe2F0M!86*yi7&V#Q4ufp{b7uuC&R{=!46h0fg6g&$)2|Not5k3q|9;@SlIF1EJ!aIQ@!JcpruqRl8drQtAu@^iV>;;a3$Aih^bUX#eap1}Dh2Y8H`S2X@d~h~=J(zqQm}<BUbu9#|@EWiRJ_0`mJ_4?T9|hNeYjLg;oNpa?JG>TLi}u9DcD-rWR)}~DM7#kaUJVgvK*Vz(;;9hvNQn4#h<Ff090L*m03v<^A|3@1PlJdTK*VN<cnw6n5nc?gMJ+Z$C1_iM+G&5g9{sJyTx$L2;GE<Obz@kFagk5ajdKddP9CqjmUvtrd9?0&qfrBLZ(U8iQ73W_UEMrTOY%;-+IB*{$p`A{KM-?5K1?@9!!U2;lXUYq33E$6TQ}Fl8SpI0xgLmD!wV(nnjzi*S0(4VBHjW&B01L{@m6@9<XoS1n9DlMWifmsINz?hcD(};zYP)3gNTzM;t3G(2#9znL_8QG9s&^$hls~R#M2>S6GZ$LM7$g#UJDTyLByLO;!W^;@Fwtfh<F|R9m%;55NE^R24{ok!{<rPeT;ZAJXvz?d&F_@36gW4B#wfQ07rqn;6o+nK1?jZ2TRT$u_t_p<lN_pBjLj(=W~HL7Cv5bK1YZr!l#2Lf@i@^lJhx5ycGVH<b19X7r>WG&gUTUHuzfbHgFBR2wVd`2Hy-m20jYk1m1+XB<^8XH@iZ><h>x`J`nK$h`2vQ903uBL&QDd-N9YKAvk9jFnJ)DJOE7Y2PXFclly|Z!h;~<&JeLb+!tJ7SEXJ1;O~LS4}!_7!Q_X*<cGlIRbcW1VDkN7^1Wd4axi%rn0z<50{$*UyaysKg@|`T#JeEk9q`@YK-5?3rwjV-f;rI6)eYw-?*Xm=SHgRNd!b$$_rdXd;Dhi1;Dg|5cz<v;_%J*Id>DKP9u7VPu7dXj_e9+_?vCRF;QjEf;Qipe@F4JBa5=m)xHIOd95pOOT?4@Z@SWfQupfLE*bnRj-vRak`{G>wIA0lfH{2KOi}u9yS!e%hlY+tIVG!~6A>w`zabJj7hKPGZ#IM<9O7ZXv?ew4iE7$o``9)d(AG^lCbp7nq|7C@}FULoyDaD)WVc(QJd6T<OGcElaVq8b)'

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
