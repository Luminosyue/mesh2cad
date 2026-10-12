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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3eac61535005406885ad708b4eb375e9/part_005.stl', 'relative_path': '3eac61535005406885ad708b4eb375e9/part_005.stl', 'source_sha256': 'a27ff4e39bacde3407e5d4ad428d845c8b923bd68a85395987529cecd6e67af7', 'input_faces': 188, 'input_vertices': 136, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11020374298095703, -0.39194002747535706, -0.03110029548406601], [0.08130645751953125, -0.2804256081581116, 0.09941892325878143]]}
GEOMETRY_BASE85 = 'c$}q}3sjV48pl5Y5itZ)ky?Y#TX;c~Btp~}6BP5(;AK(Q%b-9Y%4G&&1cBkAwPju+E7M|fO>x5;qTpp^TFX3{7OqFp)I}@TZ9Sb`tu)(e-+BK3acB1Ip0j6nJkR+*^YeM1%lp0GH!~O~dHeLx@am(Let#j*5TI#JdqC@<6{edDvKFOVB6ISVchG`_J6|rXnL2Zdadro-P%8;fOSddChsWvRqcdW|BlPf$TyudrHD^JtIW67E$EPl_q$_U8OwCJI?*~SWh>6fg42sZ8_5bnZ@9e=CbEHLy-qd>DsrDy}>*Jk#@Rh^zes;ZZ$J!?F`ZK~!=T8f_ovq&~-0P%p$JM26q5<P}3*U8ExS^s@xUJ+G;xGLgyvJ+8wct;8313wVe*J`S!<~kAg-2%#x7|63y374G3;!Y*{rDb7-PK>B&#v8t>u+q6c&&F8;^XcflDLLK%++!pbr0PXZrga>v+fr+!26y+-GrfUxO074Irz{b%(Zy8aQmajFxOYh5&vo_@|>M3@p{;J)D0bq_~aJsPwLv&g}>EDxZ#tlo_Rupg=?1^FmLQR%v;zMys8Cr6^0}K-M<`^df#kBd~ycny0=ZZY4}FOUo@iswyB73I3V%u)w95N^%ri7YeSzKhobKAhlFb%Y{5Qw|L|Mk{%y^YH?KyxVekGog*WdNu7BT%x+{&FgkRe!+%&<4JhiRp^X1vXwURUFKQb5b58rB%yaVg8KX=~SDE#A9!ZoW2@wHX^h1Vq_e*g2r?fsqxuReD`-anB6p1&X5w^4X|QWoxuyHmgyjudWNHWhRI=m&n(8{97!{eM&rezSGI#97`!pN~&z#P!V(ZvVCt`&`)!ezvAj`0*DdPy1(;;JdPfn{MPI|Ba9K2@l!)s^pEyJ|pXDZ#D_nbA;Osi-nv1_~=35*4rB-esQUA!`AJHw|*epR$e09);JjPZC2riAxnfisx9ELTV9boH-2uF_<sA4C$>Pi{nk&y^)-KP#yKpjkvx|*^f@91dFpb7J2Jm%_2{Q=EaJ;<3D*LzAdj)CQuvv-(a#UhH+gVNjd1<_1jL)dh1>sBD_px8c+j1jYSy8ji`n2oYbxBi;nEE7ye6CQ<ekFXPyCF!!$XA|R_s7OyK@h^bH}_5$e&z+cw2S3d!LR}AH>_EOJpAt2cXXvd$G?u#qz#21o5A)W}bNArt87DUZaj--u4+*iSIZB*Ii3MeEa4isXJgG;)6cqer9fSs_Q;&|Nc}1`gsSu_66MUV>jTu{WW}hyxTdnr%XrurGPq#pSK<7Ji89@y%+3os(zvX@eR2+&r3E7H{8jVc+)3wxL=Nh%Jah!KOOg1(6`8A$`;;Uutwtbv)>|5eT#5I_Z-BJNCVe?6z;mOb>lGP-%~7~OZv4_xQ~9;-xBWkf^bvVclf;M6=4@Xb^ad7!~4-b@dBPp-=zyTt=*32*tN@e9)6r9+_B~Fc>espx80q$A6||8+M#a3zgdC!gP&uck3O<V{{Q_;!VTOvy>T0!t54lP-M1~sU)G4{bI48M`ren2|B2JJ;NE+s{}+2+kofKKnD=X6;Re^|qpfIx=(_2`O-Va&9Y5pe!u5rFJ<h}9KAwE*JJ`>yOOgNDI^o*-b=V)@Q|SM|yQu4WZfko@EpFUVU59@1>eF!D_X)S9pGCakIo+LWj_1&iVG;KKu`h+UAIQhK$_c>!U%H8XD1Ql`@ALfM#(C%@=hqRr2Yrq)W8WgX<6JLk!~P#QYj@|4-CHs5du_GSS6h^D`(-ouYYFJ5a-?w6wl(0Z#$w+h$2NHEL;V=D@N-GXzp@o`ZR+)={C~tO#1Ec{K0o;z@=U8l{EYROE9Ex6cNK4F@Hppdc4Mx4cJ#UD6zcj+OLgat>(3+qD`xb+txmYjbsj#yf_|*^$bUNz&yAk^{&u$s{N81Jo;Ll??#^w^b1+xm5RZ5}KQ}c)+)Ux84>!1<e?!aD$YVW*>rz*Q_zTZsANrp}{$5$A8$Lqr2W`ta<l*<v`{$Yb{`njijQz1*1b_WU++T(S@X1$@pVv_{=1&&wdkyjDa}fXFPnavIAD&xZ&jcSn5p{137VdhU7&2^_D=AL6A@2{kjxSfB?(sz7_n#Zaz}d(<3;BOD7jqp=MV{A9!X4RG>_h#0obw)4!fny7Al@31Eb4dx@%cx<^X5#G_$POw&$blw<CTIu>%Kyt@imBd^iL6<@iq9W^`6f+|51$|`_`<bi#FteuQ<%-0PpLIRl@bKSHYX-nuOavZS<&X_%NZx=<(}ob==iy#?ESolyz3WzA{qXetJ2fY#;UC|Mbd={_lQz#m4@>KfR33EmO9bx{`jnvQ^4{MXjR$oU$d#s;LX<KjXY)%4SlF=+9ABu52#VM&G3DX=SO@N%UtZD^xa>nnOR2YgSOR=$ErrC3OY;Le?swR?<&p&MayP{c^_GSZf9I6*4A=YqQ*XH*szg*F3|Si#T@?^UmSSHqK{b-Wi-Nhx5B?Ok&MS)~jScPJg<xd}Xt!%jnNnR;p|PwT%8EWs{YqQK!&PQC6UA8a0=GKGzgev+0+zRt2?~egSJOr&iEUW6o^qa{8r=DPyf-<||-KF4tze^}dL6FXEc%oOv1NUdFuhIdd83D`Vai&X&vhT{Wh#W(Dh2upg(Ntn683v#DnK^ORYY{gRqVf4s7%lqFCN^v5ZiplmEPk^Zw>vy_@d-^yAR>Qed>SZgBHLO+2ylc*EvTN#tdT1%O40%H=nHp#8`@tk`+*CcahGv_ul?>x?&$@wywcN}L+<ovE02G+E&o`wB5{hrD?DC<u3q93fxPgyT&7y8b}=0lqE&sxxj>GxLFP1z&VAo?A+Mx%D3@5frcRE>T&*6K?2rT+kPcA|Er@5h)ftfetuH^u~UZ6~+hJ9F;NT+@>?dvR_r<_+e|T{vGC=Izbdf;hjc#>1@X%X+@-$LWVF>#OWhYCrk|l<CU)Q^V*7D*J`90BQ*R2bFbH)`RLpzc1JHq59L;Su2#<hki%a@}`E;4`5DzsyBU|F=4FLhxs}(#)oVD-Fgq?+<{yZ&YAmh?taWWfHQ}2zA)x}khA%4epihU)(mC6Q1;{W2P+$*Y#?<I{h`Vtl?|sx(T`U4n6fzPNcy9djZyX_HJ<(uu8E+=(2r!TVblovV_0hxbr}6P=8U0^q94haDAtN#zA=o6=h_&z-lI8pG}jE~%!4@hAm$y)nWH#g6!VVeZ1J4mRbwP;4r9Gx?8oUpp)6L}2<qeXjgvZf_3-{re+vKS%O*Fg`ya;tb*1OmIQNxhD%brlb;d~@<v#OL|C}FAot<~A_77%n^3e'

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
