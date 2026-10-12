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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f0742330720b49e59740835a12380219/part_004.stl', 'relative_path': 'f0742330720b49e59740835a12380219/part_004.stl', 'source_sha256': '1887751ddefe6491453fefa3abaf0aad1a2489b547591040de9e1e97b70e0927', 'input_faces': 332, 'input_vertices': 218, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19700555503368378, -0.0828835517168045, 0.18520870804786682], [0.19411197304725647, -0.023461800068616867, 0.22789382934570312]]}
GEOMETRY_BASE85 = 'c$}r03vd<H8ON6dP#_TuK@d@{R16>wC4uk|y{KR%DiOpW2;KleB9K5rB5y7rD2R#z0xD!72?<XT5Tl~5sCgI!tDvZ3=UQ4?tys0K)~eI)+4I}Yo|ElNr@b@Z{D1d9C*S$@J7-@PGBe_vCL8i|xv@Mtde}GiR}l$DvQeB<Fei6%PGRr7S@W70Z5&^GTwQnjnA<Y%ZekQ03sR=!6izNk85ByncItqXo}rYf`2}+dvh(iEFPM@e{NdR%3Uh3~a9Z}P9Q%8>zSj)s8A|QmGqfo5KYm);B}C?@*S&6Qw8zLDLX8h*y>q=Sq3&spZ#6F{_xrJxy&OOGc}j)f56|u5_~F+^IC-oW#s&JJQ!5nTd}T|SKaY{pS=N)Wq}-oJ_uV|Pl8a@Yv56J_@va}mcgIIl+sWf9{ameoPiyI~db>=iU-R8Oq45chZ;TqQ^v&qnQqKGHTBUDRRWmvMi9Jf4y6@(9{qTwJl>Fwhc*l=i_id?Cf9&U4XI-++DgBIf`McvANre@G{!^*S@#?<Uw-H}Cet7<bN@btCdDiix=Ze&IeDwE@ANp-#rLvBi@8&nZ{LJyqQ!goXMkb$@^M0ECf}^=h72i5J>yR_P!(zpcZQOXksjG93TEB1N$EF`X=J%t?Y0{q%tqt<Sy&}r^aJQn}&ivYV13#pVw=Une%UL(Ao(R6B)niutB-gzvUpX%G>6ztzKb&+*=IMFR>4SMkQk~xq<68rd*Zcigg5mh#TZSv+EqrU})5>_O^6TfE@qa#46XctpbgEVA!H?Fzbxf%T-!QLw*YBI@pH&3a6UEo-F>)3-{fTPFYfX{9$?=AM_(0D4?c>V%5?g&jj{osYsj~ky-`k&;)yq6_1Jv{DwIgyr?>nmOTXR&EtpD&u%Kq1VH-F^pL3v!S->;ls=JYbTUc-ke^F}jE1J~X4^>ufBecfGOUw1FRwvJwYZ5>@-UoY3!*UOt%TdzpRZNcX|exvgpztMS(-{`#7eDA!*Z*>0RH#$$<dG+(u_4V_#Zi~#rb=$kYXui82j2kvdfBQCN--dp-O4ga3t?sw4mq=f`zv#Yq|N5y&?g#4!C66^EPxk-$BkJ`$d6IIS_paxf@9pOkcPjT0ug-xt$$8HlQtoT9VS}XK)==-`n(y6@()&pN#tfzYP<;<sf9q=H{u}AnQTl7wD9;tT@6}(@LiT@AmXgQ#B~Gqy?N#c1`HFwmIQ6ifz5Z*y*Z*6;mHzr_wGTJfIDT}&JIcIfx#jp~`;KaU&G(+K{!}INAIw#sPx?LS_|}Wd)#sDFYaBmpeWdh9_r3mK`H<sB?nzPdM<2_s3F=#9$V55sirs4eHQ(#cSL5WokNr!@6JDJz{m4+&&+jjf_vB_JzwUea2d2q7KRc(^*)7@eL$kjK^sQ+d)cQ5w+dqkI1M4(Oeyn!Z_m=O}=jv%cIDUBORwcjdhw#1oQTxBiJjaHqd6u534(gkEb*wt5|GMw3?^~Z%2k!r`-mjM56O?tgmK=BdSpQem{iFF_{ZrnRb>7`;r&6cufAUx7J{bNuCD1nxR4KmMFVpd3=f0@(`%(PxmhYAE(TB&%>rB%(l<^V#=*rIZ%Dmgs<nfjtP{xPwLuY#_<BcoZl?UaIb(OxJKQ{N$vY`4ce7*kg$$6!L{lVA!V|+1KxsOEuQ7ezPcdok6k5<cmay{|Z{jQ_3Z(NtW>%ZoE?=Q!X$o>=-tNU=%%hLa*%Z?!5`r~nRe`>zBf80D;exvjmdA#cq_67Piv-dihzrW7!Th-DJce=XX?}x`)&htR{4~fcn13y;&zA`>`O@C)Un|Wrf-#1;qQ}~#YpZ#NfIA0lW;71STDC1)b(@O*MyS|?P%Stn_etf-t>-(>_IDVempD4cGAG80_XO%veca!5=r0x&$BMBw)x$&FgI=>&r4?mMz@Ar-IGo5v@%C^_~eRG`jqi2U4^ZTLRot)>i@TKjP@m4SC$7a?m<0EdL$DgV3`!N&0&o9dOX!32_gYt**_55aqu{EfE13#kGADg~@v!j1e`(xtk{jnxC-{kLec$nN5`g5}D>(9xquRjmFzWzMy`ug**mtTMGeX3Nx7wYe!_>JB}@f*E|;x~G)bo1-)mH3U`AMqQ#Kf3d3?<2<8Q-SrnzFxoU>-D?7UcZ-LtKaqY`dweI-<wyfKfLpF@P5E=v>)&r?Falu`vJevesJ^q_d}-gYw3`pn(y1RF$@tcjAUbKw(qA>VTzBd!9SJeru|nxm8Pcl{eOQdy~(cOb~|n(1mB1bgKva0&|BdQcqn=UJQN;*{u&+uhtcccFnlvQ9KIR89vuP;y#)^0(aVm@2*EwkE^try3iN9D3b-$NCEOQIL9c;R;8gTia4Ost?G1N@`=FP@ec;aMRd8pxJ9;VH9qxqofIGq6&=4G=7lI$P<8eD4L7#vhfmfmH;8pNLgy0qEdRXX_@CtY(x)xpuKTHT-jXnmihSv~+%L&01=vue}-iba5?}T@w>*3w-UUVJ27v6(D0q=o#p^wA6;7asSxDwuhJ_7H6%g|MD8N3~R2;L5x=nB|`x1uZIt#AqYFkAv}Ls!Gw;8JuAyoO$v5`teK1iy$@z%Rltp*!K1;8)Py@GJ1E=wA3$_z1cOJ_5gt?t)*2tI$fg3O<bPfDglm&@%WCd;r}JAAt9xCcGcshi--U!Ox*3@N@9<=r;Iy_#j#em(pv&nRbk|;|@ab-F9T75p*mZfhQ7z??N+Sq1VDA?dV5tp=rLk(ikhWKb#3)i>AZp8RDM+4WkJmxEXp8+zd`4XA(J*@cR=NkvARgfF{5l;I`;_u+R%&p{-z{?cla>2kOqE4-?UQ(Jc60IGf0#-*=!R(JVNNyd%+ccqH5p?ErV6o_<6-dXokxp{?K~xEXyG+8k{Kx8nGl6Y-1{YWUX3pl9OK6h05W08NB1fSaT7a7R1DBTIWia7(lW+!Bsst~heX;Ws5(kUJ5+5N!ir2q&W*VWF46qK3hELI=Se;Y-i~@FnoY=s<Xe9n<WXNeIqGr@*;z4tfuq15ZHjgeSmbsBH|jjKLp7+(|71;8Ey3@F;j3It3mFPeP}`li;c73|Q#>usFuqcr)NxXc0UMo`V*{bKtq?e0VOr5M2x}grn#(Sm=X3ev0oxH~IK!z6*U8o<V*06N2;5IdC3afX;;r;Cbjmcpkh6jlzrIrRan3Qg{Qp3Elv2MxTX+Zh?hvgoQ4LH^UpyCBB?Xm{aHiUkwYWQRoA{njhepgckaav5+1J&G+>rpPmVw?(5-ndMxxlU(W?kMJK~k;YsLtqhU`99*2%L8uqYYvBw9X1JTh&!};0TXgGfbC!^=X$*{O)B%<-?`EWe!egwy%t>HMhC3>;Za7`239vx^jTmuCUMn}Vg;W6lVcnmxNooqB*D+K4D_Zbb>7Qwmbbfe)~BzPv8Z!}!H1kXkb;n{Ez`T$%67o!W{Vt78f1fCBsMwi2j;brJXcp2=T$3mY$H^M@<!0+4fjvXJPZ^9qLAE5Q{aXYH*_z<<=58)Gb)Y<VHJKjJ)g5Q8^&=c?p{<elW#9XJ*qws0?J+u~n4?cyy4xfULp>M(O+VQp>C(+m7%#0>+$?^Z`zg{(bqRx%o{~xjRzf^yQ@c(6R`$5C|Q6e*=nYh2(CqSIDS>}niR^#7!gwlW'

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
