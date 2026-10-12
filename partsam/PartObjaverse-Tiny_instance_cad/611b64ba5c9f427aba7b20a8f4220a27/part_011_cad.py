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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/611b64ba5c9f427aba7b20a8f4220a27/part_011.stl', 'relative_path': '611b64ba5c9f427aba7b20a8f4220a27/part_011.stl', 'source_sha256': 'b9edc08ebea0bd0da437fb6b445f48c599f1166f432e146c10cb602f50d41937', 'input_faces': 232, 'input_vertices': 170, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.007388278841972351, -0.47038042545318604, -0.24269786477088928], [0.4357196092605591, -0.4084937572479248, 0.18569661676883698]]}
GEOMETRY_BASE85 = 'c$}q~eNYwG8HX29)PRa#O;BUDej$peAki2s8_=MFO5-OM;{^fn8v(5-*o{#@FMcD4jd<0dGCENVW5#$JcGLzNCrzEfsnIAK65FJ-o&I6l(5mUa=lsrg&-Heu(=zkU@8R+A-gnQQyWGLl<iO7T6#n%?rT5vS^Le3)LKUL)Q#NMj7p_>AT@bZ4uP8tXWuCr79-KXYR%%*+vQgO*o|Rp&EI)j*8XlK3DLhgQ&smpWn4htB>AL)^Z1S&XtS-p5d_itTUbgl9$ng`$MXE6ok!p$hKYl$&GejnCZL-2}2i~JpKYnzHQh8@E^GZngU6$wmSRT*5|3?XZ@2dDG^R5%^d_BBY6vezQyndT`<LXG>C+Nn`c!zhPzkV$CrgOap@5wLmI=u?-s=LYir&lm<qQ9$arq`eMG=I(4Yl+h9YQIn7uiLqynDxIljL-Q=ET8l1<;BuIJWkrh{EflP>m8lseS?2yf8d|lAK}G3M;3UUUR<vcYs&pGr~2*Kn^GTmb9SNEpI6_y%KNNN+~Vw`%}?Zg;&L}Rz5cs7%<JRR&c{2hSKGO;!Rf{IdIqIPUd*p_BuHM&qfH&oebFk(yT0F4&wlP<Df8k!Y84at`fmHA{<=Dd`y-XoJnHRNxR0!n)@y&i!~1`9lzDOf&F}b}O4})^kN(>*zur^&q+as1m}lx)=Jo1Ed7j)x?jtTs`{}x<Hu&|Kk9hxCSD9CC2k<%Fzu<k=-;}OP9lDLLPi~X_B!k^|eQmqk|MB5^rx$aYjitQLr6<yTF;Cv(eH!~;koNy(BlFtIp%<k4`{z&j`ieMdz1jaX^R9%M(t2?|_0f4(;vMHuxpMGh_V3>9lGh%*%e?VnrQ|)G_b~6uJ0W@Fi$?B~>zP+JkKpGmu$FoAz!iCYL>cct%wS%;PnFAOnb)WPO7ePZC0`%g^#=3UPbGF)6+6ex!OXj`|N5U&C2v1xf{#ev492+~@|?lerM<wszCY{%+m~Zko1NaA-k1Atu1j8j(0<>qAK7-_Z=b5qnKzGpD0wBPCqIWhQ?5&W&UfR_!}bKpn=Sm@>ctzXoZjA_>t&Kx@tpMa9`PJ#>?!SoCf;{*&&mD8dAmRJT9dQCcn*vnQt$NQ92$Xf*Zg_4a*4EF{JzlNPpX#oNBE>bHmCZBVccID!0wBy$4AXh?|XkeJxB2V?yh{FCrr8S^uFguc;EA*6h}zs!L`6>c6xChp7A&j<~Lr+`<`dv?fV6<dqzp;$MbDtv(t<7qn0GG>oS8z+>)*<B(u87>BZ~*a*pKf*M(PW;Ke@7e8jvlXQb@6PGMeY<6b;hm9GvnuN6kza^7F%yNttZuAou!JXkNhJrBGZ6vez*#Gf-t<XJwycdXps^{9%y?x+~a>*{Fsx@N>g+0QHFbDD9oU-N{|vpA^5d2Y4TEPNj5-r{^;h|gF0)?U(j^{Yk98|{6h^=6lR=3NuQr1kokWWN6RAZfi;lf%5(QFKST-l2Eh^u3X@L-x&2`RA(+?(Oq@@hMxcw3OeG-oF!n!#~f!+w*L@D0#cT`23l(TkiibiO(}=FZ1H_hVsdE)<=D9pY*!MoAr{n`>Ywt<~NotxXb3j`&VfgUCVy{RvPmv&cE_mA@j<Bbmo-{{Q0T3rheMw@CKf%%BA+BtnWGQb@W%eB(U|uyWq8$V6Q)~V&8<f=X_Ym`Ws;`-d{ZDQ|7V$!rSvt3uW^gnVGylyeA@&uZP#f`@Oh_*RRJs!rT43Z)Ni+4Y%(xU(KH<y4L>``}x72Gw;FkO8MIm=8c5Ad_A7G`g@_0S7z|%p<W&?c@Lh4ws(KQypGp(g@=6B<nUr1<#AgbTbJ-aTJLG?_;r)RYr=cidHs3wWxfx>+t+))hV@sLxAOT9@ZbAJWiK|5@E&{~&>Q~3)~g*@AHnxWtQTJFn^>>AO+G*NO>GTe>xFm0+w;R~@b>)h_Ws|!%=&v?{F3*<{%e;*S%2Z}`;z!qX}!|Q?~Ctx`+i})a^Xw)de=W?`!BqGPKKZ3*W1!2&r|h1zhCegynVes-o9RVF~9P`1*yM1zfXS?^ZWJ}-nYNFUf=#EuFJQNA%2fjpH%6u6)mHBuW|)jmu^*erJs_M;rLSpN%|7$|4$VwCj3`_s)&w>{(t{e5opcO%c@Sup5RVk@kQJNMf^PS1@QA=6*(9@m~9DX6+9e8JOVicJOUh!90sNw4Gss7LJ?0!z5<>Mo{F3XUS?IMRq03<nDQs!bnrst8{jw4V<B=Hcp-QZ@^vufbTH*y@FMUM<WewY7B~yDE<vV))A4%5wN}+x^{!PO<Z)yj_&E3k@)Y<4_#}$>v{lED^~h7;dhi)!9k>p2oIw%qv8u$Xx2@WOB7O@+T!GvJt^ijeYr(a+o=Oz)J1F8Kj_W^yB0hj3u0j!4Baeft!H1D2z=y##$dlk2@Ie&u&r!rjk*C2&!G|3CdkDE7d<eW7MZ67J3f=}TMiJ{M;-6Wy6}bah3f=+Uhuja|k2&@s>%sfLdy!|rXK-)!BHsq@1#d@|fJ-pbcH|E54!j2OF00&D%|j8-w`u{h9O(v^gT=nN9sBIYeQ=|%xG%dL_ltNZig*rk9(WFT3X1qgDB^hJd~iHibIeVgVAX3@r6D!2hBav@;xc48xE$A3hTIJ<18+ud15*}*DT~0H!HbbU22&=26EW*zWEwaPuSYz<D*E*{5E%>}2%d$U4W0$gMy>->=7F=p%aMiP<=|Xo0hn?Pm~s_37o3A!0nPzupomkD$>0?5IONM<${6rCa1?SpI0_tzBJPVK?t_d5_W}2}>IcXP$Y}6HWGpfo9F1PF$QW=8W{pJ=PeKvTKqiA{fL9_{fLDT7BUgb}VXs%Ch}WWs^N|JMeDFpT@lR32n~;UzP2dg4JTT=t@CNXD6mcqYHaHcWgd&bZ5r-gy!6D$zDB=JVaaUwNa94156mf49aTsy{I1D@pMf@U)_$A~(@JryKDB_VQ;#ZNgz^{U*qlo9Ch?gR>!Arqe$mL+lTrg!0m@)&L1%4AnJQJA$o(Ud{90wi?9)pYmQ$~WvfFn@Ep~$}AP;fUCaS)2Q3$hQm3z+^NE;TuzQ@_Cf^k0ep{?h5@OaHOx`;+p=dgo8RXZ5l_<fkTgp}DLN(4E+Uok1r+`4^bDaas'

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
