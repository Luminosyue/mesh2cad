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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/68834dab6d6c46bb8fb7ca4d5c218b67/part_002.stl', 'relative_path': '68834dab6d6c46bb8fb7ca4d5c218b67/part_002.stl', 'source_sha256': '54446a8c4ab399f23c9435c14809345e9101f33bb6ff24179897424898c98213', 'input_faces': 224, 'input_vertices': 184, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07303063571453094, -0.45629191398620605, -0.483028382062912], [0.3328684866428375, 0.4150644540786743, 0.4587986469268799]]}
GEOMETRY_BASE85 = 'c$}q~3s4kS7KR%Y6G4LybcF;Q&<z^IL>`I?I2zxGf(mK^I)sOaiab>?m?6OzYJvi4@UbHXR75}o#KcDjO;)0?31e7A9ML4Tr76}`cT3B)wzm7+zdPN{Y}MB8RGs?2`MrJbx#ynl8OG4yp1mA7_HyG|y%J~g12|5MzMLbsE-p2FWlUV!n55)P8?Hb3;!DzkdEp_UOKrGy+(wVsxU`s5kBK^ufOvn8(K?U#wW;Z;(MikKrpCsJ{*36=X>o#|mJppBC%hjy*57xu&S%tUUAFFjeA$VqxYyKN5_8#WJT_U7&VAD@mlVEnQ$(Za^P{plls=d1(oFtA`*zj%oTsg#&$$=1DSf_pcAMzyU2n9i<_RylDf-6G!<tp&kIioveVu*lWg7RQ=``v2XJzDjb>30=;|3ikKfc_e^o{XOl)wJAbBD_RQz7}r4YyQ2S9a|>`MuBFQjIT8ru}w$$F?hdKJYTzZ}zk{)%fTUW}4@%UsOJy=16tWwdA#`)?M}y`Mlp7X4UxfQB)tkr1`pPd|orFo2$85H9p6I>ee|hR#i7+Vm|qXp86}|dwtl`Dr<F<d~JPXUsDI!*X&oGU$ZaS*W@qHqsfy?ET~lWk1_n$R;4fX5BI9ESv4O0!)J1AzufRjYke;H+CG=ZYx-OsujzBi*Y>$QkEYM%@tQv8hhDBw){R@^V^;a7n|_x~i_(|s#-%2)x-~T%Q|&h~!J_o#{T|QjP>siajXQkXRpYT=Q`Mn1rLUjm#?ED$qgm<mE}PhX_tZA4eC*fI%a8IjzSmW%>_fwk%@(CE^`YU}gASFCJ~V9J*{<@@hq{KYHl@$oFJ|ZRJkqRMcVRuNXXyAA)jX)D>17G!$)BBDVl7X}*XAkvnmlD+lc(fs^OV=s<SEai&GQw9Bg%6(-OjKmed*kdPWwAl<8khWms8qR<8kgr-N`nkFP%Fd=5AK{(z){$-#4p#oV&?2jP>V=4^3A46Mnb;l*ViOQyQ=BPx#&X6Mnb;lzeS}uF5{FJa^rU+ZLrSox3jKS%=EUxtsPBx2t^VIr+^$+mya^?%c{mvua)G+`SjHsOFKLla>pto?X-TS<6%MwRy_ECQsSd<SF^uJmqyYdCK!>^9%|vRQ0FZW{c97&fRq8T!(7Bbnb5kx2wkE-1(C?+LXTZ95&exGOOmnb6Dz6dAznigG&pn-A9tIy^rMan)^r|uepyTUwa=(zV<$neQlmG7xR_p-udW(Md{1Wr5;XqR6fpKuRGeV@^S9^+7W+N&5zF`<E8h_Dqs3MlFnV4M|<v*UVLmdPx#&PlzeTTlCRBEnqQlz<ZJVk=F#T)x0Ll(`xAb*{*=aR`%@aP?N9jK`cs-m+n>^S?YVQc&x1ty$%obJACY$^D}2*^H}X554pI5s{TGzC;c-p}t@F^Of$DPa3i~|xYsYPR|0wVrozuN8w$I0_XuRq11@d+GIkxVTDmIT@#@D2G{&Ji4{nIn{z06@fJ6B5|Hvi9aZjnEri`CKM#PazinS6d|*A-g#=5eZH=MTGX(0VSm-_ks{n%U=5>lO03VOz=PZ{20z&&(D!-lO0u&2L`FzQ;Fae^28)>zZhPH?qh#G?p^oYtnagem8cK&o?%Z-|3xwjkNh5^_f1h-ydn-@kiO;2`#;EioPx?kogll+4sekA>`|$!r%uo|LQ*WIhq-Ck**JlX`y_Y&Xcd(_$l-C56Cw*U58&ozP|kF4>V7>1MB1U)!S*m<<H3H7L~HT@$bx_^~+z9Z=An_{(j)s2ArbvDYs#L8Rkjjjqx`RFux!BUK?`v8eJd$q>ipDcVvF>a^|nLe8qfc^7XTS{f^FSauiQmu4Ch8#*wd^eXfzNtH@=(|B-L$`smsdv~I-?mCwz)T15X|v76=TXT!#axYn}qg({yb<YVaiQzh&<JN5zl{Em<KlJco2V|k9f%kH13=SB4X)H&vRM$z|geOAOJTIW<7n`d~+*ED|m2~vHf4f|Ylf1CN?>1DJ|r5$@7=?<~|&q%7V=Ih6gq~~L2B|cw$o?M{y3=bQu`NqinPw0KsT;>mJqj6luz>Alx`1+iL!?a%YCg$75Qy#i0Rc!s!Jo#K`({9q~UUc6Y&dg!=)3(IZ)URvCeMMT!?mupGV>Rg%H=g>fuA2E59#UU&DZMFQuC9*x)md~spYwAS8{feE*t>K+H}wvyQ{6-IjVlhY=SM~m?Mqkxl#P$sPUDTn{<~;j^?zr6oGlw4=1To(sJHu({1u;(FP}^O0OnVhQ$G5|Tk0sEv%cgT6Eo>K#6@f<V7?#oS3hFkKO>Ur#d%C;L)biP3ogs^hpK-4=`4OUpR*TGh(4Sn7ay(o>4*M-<7Bn|)6YuZ|LUh7Z}0#6r=KdZB;xIY5V;0g53T{9fu04Q0iTA}flq@gp|#*j@JVO|Sk!WGt`Iq5-G%rFx(S*C-UQA@i2N}^<jv4r@MiEf=vMGH@D6AmcnA1XA$CLah1e;?XF}|P=7aMwW*0OMyc4<|ng`wv-U8hU-U9vvnhVaw{zX0^gh_}aLVOP04>f`JgZDuXgZF{=LJxxXf(xO=;6iW_^Z>XBTmU@;E&%UAi2Mg3jzi0!hrngvFQ5m&Uw})X#o!X~QRqSNQE(~rFt`+a3~B<KP)CuIgjgel0U`2o=xXqC@G|Hs@G@`|G!YyHj)blRM}psnCV)kK54={0WFgieL|zX~0j~#dfTn^sfHR?K;7o89G##7;-YCR}&<togI0Kx7NJnkbG1nSI8fue<wO1ojQJYlcx(bnk+N5A_iHKy>CK<I@2~7Ym5F$*7X$X<ug@%IP1y6;}2Tui0fzAU@0qdb5U_E#;bS_xbAn-yV76}oJ5cvaWIQRo_3^W291CE6*2FHTqpi97U;CLZcK$k+7fR}<7AeNvuOE6a$Vlis77;A?jB2b$M<T@V_j@pD{Z}Sj~P@6@lMF?~*c$^S^LcEO-c?{GSJO=Cq^#OZ<M?<~Aqrslgv0zW|ThMpFqK*QO7s6kN=?IZ$Kqr7_fM-G{f@gwfK_`J{foDSlz_Y<~gb0QPLIc2o;Bklm)FuFP`5`8uHj}WnFJdBUGZDG^ASR$T6R<aLgg<KIk6Mg{z5{+$2pb{npgq8L;J(nF;J)D3puNDaf%`*k!TrGlg>Z!ShT4LAg9jl*9sunH9sqWL_5?eC`$2nv`+@DDHeh>jA0b|Wa!?zv4eBDk1`9Dnh+znkb<p2|bznE>P_P@=9qI&j2M>ojgNK7h2=RO9>riL#>tIKOGivFKxdtMfP<tn=EuF<soYhd|DxICkeW63R-_BZOJLq8WVAMzCkwSO~;ffI11^On~1^k8(p}{si9DDw!|2qBcWu(JU{zt0zO7+)n<(2;u=90gJhX&h<{UtO(5Bl(#AZEk;8$~qo2>'

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
