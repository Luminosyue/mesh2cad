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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/67e2e51a2c87480a999293f3c554d61d/part_000.stl', 'relative_path': '67e2e51a2c87480a999293f3c554d61d/part_000.stl', 'source_sha256': '268f22befc07c6bb1ade64fd9a870a9abd273e023ef5d4cd2315d309088d5c96', 'input_faces': 196, 'input_vertices': 134, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.21556687355041504, -0.292144775390625, -0.1483985185623169], [0.2155461609363556, -0.009568274021148682, 0.3715592920780182]]}
GEOMETRY_BASE85 = 'c$}q}3shBA8pk&vqKQg`_@cb20VeoBeBkq7qK*inLcSB^?E?uAd|)0PKF9_wO|YiCsWU#BN(obx^kBYCg)+-*n(L%3Elr!8vS!S=`~Uq5m^HK3teMN&>;Kz-4*Puj+k1cKTw)^Kn)oRBJgSBcNIT`#QYqa$m5<6z&dNzoOwR6+k-5l4dBNA8Uvyn`TvW^y7nQ4)1SBPACuRi<v;_=K84wU;3rLxtm6Mf_F>`)aQnL0(Cd|!FcKX?A37N^xeqirDp+UAj-GXdOZU5uv0Ubj{+37=C1M+ukHDCO^a#%yZeA06G_gd`HzEzTU3VyqCT(3rSFVVjJ)B^ECJFb8hZ+I4d>7A44S0>_m<INVwv~QmKtN4D?i?v#_I>WbyJPO~;n|cH~(nLJAF>6oY`Y(QX3z~6qEv~O^E`EnK@U0u`k0SnNuN}wzhDKu?<Ad`@aNqH5;H#dq;X4C+2){4be+>PVdnFIX<sFUu%AYVVGx_BmGVeX&M+M`)rtc-h={UMu{JF17-d6l1`E)&Y6#XF+Fupx(P;EnBrPUU}UpErIRdiVV{*z?B!%uB!<oisNJb#~9rhTJTU-6UNB%T(Rk2LbHoJO9_@H_Awqt3sFe1(rf9;_Fm&mx`y_Yb3gFX4TeclAcxH+3s~wbgee)V%a6uG_v@{5BgT&X5J0aG%FF$vDlTWSre$hY^qKvKsVr9d9DPiJ@m3`9TKaG&YWc?--d2-~4istYg%4<j+btX~7@eqXK&N%c_RHGCoC|#<e~0?ceNzZ%vMqeHRvf0Q+jsR=Ga;i0q?lKdi)kFFqyy-Q-o!s-H0*V{L~+=*RWih5qI1??C@>`yk>NF#_?$*TtSkJ_B#USF6fpeIsXzzdo!Q{s38Dd(`hgL>^x54&RJ0FkgH27at)1KW7}k^{!R2&$n&Bybag10}bb^_Ge2zlJ;ZX%6H{CXiRV}?pxV&ANmESk$+pCZ5ZFNH&FbTX2`#-^;_`G&QI+{92Xz0#kjpAYA{aKFwEO39gg)iF4kbZ%=Fupa=vCte3jcIk1uS2Z`Nf<o_EyY{_2%d_||u+XYl(eXSX4Lor~rAS4(7n7S6^zt#-RGuC@Mx)Cs?WlZa<dFxJEVUZlk75r=wWJGx%(6Tx*^|Mi7N{&QTHo_~XHw)y)T@ULH&bCkbE_D}meZ#3KwX6an`X6UD{Bc5N@>-!-eVI3drzZ3WK_@)kj7d>se_U$JwZb$#>An}tPFOvK}w5`#)^gWJ!Vjl1mfAS5)X{)V;?+DrWGV;5q@B_s052?@U>K8e<e%Msx!x48`^8aDiZ0MY(vTr*D$o})(lLg)NE#_sst;BD8Fcaf$ip6>v2Zmz3Rj;P~a38Zm?pr-)FZ!VuQm{|M$07g5jf@lU#}3bcR=eZ*V6~rk2K_?+9O(O_uzzfRjym*HTP%j=NqvaFHxKz#W1bM-=!*RrU!Eua?XScyia`Dyz3+){49tfH&&4{%Z#jqcRclL@N<4Ac4-WT(AETdLBmQ*Bv)z6izRk+q0spyfC7A!fmizH{)p_vEt6s>b8PE&9{oUbj;Cj|!$M)B-UiNol#AhA0CGCW7l-hPftH&e$_);&#Z+<-szFHQGd|K7F@LaRZ;0j!S{&({HS{)_z;`Uhh=1a@v{10f4x@iQR6+a{u^R?aDhdfw2>)<P|g%Z!Rhb2E-{w&vf6v{cBHcs|S`5p1QEs=9NYcrmMR%QsEZ`P^nQdc{8;yhX@-usZh*dU32ag_!C^ho%Y%QUGQo%_jir{oBHqhyoRE9>r9^!*E}8s^z>t$X`W17GDNU|oz2JH^lVe823MP+9ju(@@8L^%t(eb2<J(5_~oBZZ*d5pC;pP8-qG%)LuD=-+w;?dA1E-E%mU%?-2YS&tQDprD)V`wJ{35xg%ZblSjPNW%|zd1;lAR+z-AZJQVpb)?Jl6XWq!eJ}E1<8m_Ok<SQ9(`=8*e6FHLSl6PeOmwpg`^9reNSH43$wwHbse^s{3cj$fi_D^m}{mze&{d~V>GuE^0Tli*bOXNXaY_$dRt6hZWwhEGSWO*mZ`CYR_{C4slVvNoafBzQv=FS!J+<)@37j!@VxZ8X1_dE^X^q-3RS?6ozz3iJgGT(_aF^+v@qP)l5bd`9nZT)Q{|Hw!3T#osq6n=*)@x8W6oNKP)epY$4`0JzPec;$#@x!l)f3cOE7jF;Ln_qpdml^&?)P4K*=kYu-%F5*2W%ejQem<^%uRO=db78Xs=ft+5Qv92Lk>^NAjrcX6iN9{MyvMwoajubn_gUoAswjeQ_&g?cG<m7yCt#oC@k4*{Yo3(+teU(G^O{r+-<;A-_H$7#@@t>a5$DpJv0CC^)&ud_C%K=(IF}Xjpmrsv!uRzM-{d~2^_~a+e6jfVPsscH^A}|Nbt}ZrSt0Ks5jW-ivq{-$-1pWMd9O~JT+z^1pS>b^n^;&eET+-7srWM`y>~TtM&xYGo!_QX5*mD!(k8;C{`;>|>7oDKSE;am|L<3+$<7#t>utlPIfOcd9766y4I_6V+o%J{T6>ah<j!oGhf>4ITAw5jCC5{f$?@c+)Kv0P@-x)Q<Y&mUs3XX;$iHFJ{1`Qa{1~|zwG+7+*@J2$+c-DP*dxx?kJ_Kyj~u{jqWF7*JeE40JeE9zI)^-iJe&G7c{VwVx`>=bUP#R*FC^zs=aO^C^Qcde=aFYpqscSL<ESIa<H)1fG!Lc@A`d2ar#?>ZPVPwUK<-HPp*}?RA-AHoB)1}aQy(OIliO0;k=v33sR85wu3aGWpy#}VO>;VR966mFM;%3uBS*4n?n@m^?n~}U?N07W_M&zqdy(C#K4c%x-<?gf3)P$KLUvQSY$^2!=h>eeNcAKKlG{?<$Zi}*a|>tF|DSQCHYK}~6_w==AI(juZOBc?t*QRx*5oeK0pu>^Q0i!MD0vK<=2&VBIhLG8O(3U{7gICIi^+x5d~zYVn7WKyOg5=`WRtvrO>+vH<_zjGat3)mHJ_Z%IOelyo=Qz1Cva|4*)&H`N0Uc0cM)uwgQ@;xf38O`o96b^=47o+$?eI$)Cb7EWIt*Pat~+g?Q9QI{m6d2=3zF?kFaU>WYg?MbtSuzU8qXc?|=Pqr#4ab=S8y@wY920Ynr=KyQuoJsktvTRMnql&5_hGWUaBPz7A-Pqo%3)TA?|ex>(iM7R^hjg{r<5X)dA`lZ(j9sU~?jxq!NWTtLoc)11VnIgy$|o=BZQO(9PpPoid!Cy}SIX`VuzPo6>^Pn}90Pkw?LLDm{feuCVG+Me8p97Odc2a&t6Y3@b!BWvwVj)`<}^>O=8|2nV#nAltm|B?Q$f7$povEg4vJIDI<r7<Sb9d*;y`J*4~VY<qye*%}L>Wc'

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
