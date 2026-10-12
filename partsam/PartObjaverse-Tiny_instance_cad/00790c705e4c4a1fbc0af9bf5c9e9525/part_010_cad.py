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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_010.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_010.stl', 'source_sha256': 'f967716c080119db6bfe65718d068f4801dfff35f79a635c07598aa073730af9', 'input_faces': 224, 'input_vertices': 165, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15775659680366516, -0.2077169120311737, 0.15558986365795135], [-0.15051838755607605, -0.1993831843137741, 0.16136424243450165]]}
GEOMETRY_BASE85 = 'c$}q~2~ZSw8pRt_6x0B6s0oo)R1mpDBp#@(h(SdJkq{7}5r)H6ZUF_M1wjyu$f0=B-dUqY)O9U2W(*`&%$n$$O02Av9gnP<ctpixqcO|$dn8V3w`yybs;T$$`SJeW|C(vXuo+#t+6(v@C~Tb9lKs?L5R9*0g1wNZ%g#+p)a7`kXD%@lY&75a)2a2Lku$@h&4fIm&^1YylbG!~R&)(W9_{KOx+Z62=Vm9Q$7f_G>5Tr=goQb}4nHR~Aye1!XSWglqddfs!#u=g;{W(#)zN|!H=^xBqYiaEtLe=#Z4*0Gx$CX@`Xk*mU+*_q^VJ~wUpZ*Ld}^%b8^(EQzTDM9^TmEcHD9jq)O=ydP|a7o!;$Yne>rm0jpN`~dBBfBj`GYE`6<KEXYmmDXTmgJKhRzC4RarTs`>G@$O#^Xe#!=G^@c3eEAH?Ov5&QSy@kEz3!ZM8uSPwAzuyt_z3PH~7Wiv9LP#od0tRWmc-{~GzGTcdd?4}{e21Lr=E$E2U+8(`Q_Qa$d<XjP-PC+}aSzRxYDM@yBeBkdbr?6bAJ$?0H<)kZ&#hYh;lA+WF2SGsljbYmIKp@SO7q3BPc&b6-yVIQ2*UalEW@~W?XbT^f!Oy8OVOt*{lH164=8{?+#2f^aZbxu?>*A;4e$1bzx*uvF+70ZqZe}ibO!72_#XQAw?IEOr{R0uN1wJ`(f_dzke_>3^Y!P<P_H|V`rAJs=Olb(Whl;bex=r@7zkgE4##<Gt;T+x5|BS+4(grOU|yN<6*Ut3d!-iZ<ME<ZtFt(YaZjNiq3W6D%VQ2<z6)<-zD4jm=c``!#JLTDuZ;af^9=*w%Qo<(kJ~g~O7K8G4}NNWdA?GPGtOr<d}+@y<gXZjKJDPEH_@lK`E}f*zdqG`k>^2qF&_En;48@oa1P_X$9kTDFF*Veel6<d?eO*IE+XHFIqs%8QluUFDSQGyX&?MKeb7(r?|gyldHgZ*Q}<%rXxwXgK|AVQ-o>~sSZC3Z{>>ez-*1U^9`F$U``a+zL%d%z9<;uEPo?Xj$oGV=Z@7;Ay#!xzfUo2=!*A=3dQ14~scXpp5cR^7``DK$J5A25l6>E!PpJy)tgN|*aUC~dUQu}8FnoCz_4_fd_z?3IV&NP1HQ{|`sTt<m9lm^i3;Nm3`!)Lx_Wf)O?)A3~n3p4bVcI(6>=kfdcK?8U_9LC<{mO$cxo$vx2=1vq4Zi9Whxe=WCgg|17abdr^W$^ei@$u2J|ClhC7t{34_};xe&opyvA;g>m6%4X=SsZK=x^MDzj7_^(FEk{=ff8lC!imj&DgK}o0#t}@1XzYXUKmOzJ6pPK40!^!8(kBFWR7gW#W%oz53A&lN>|We_|hN;CFr=>F37dywUGm2chB)<~tg`{I_<@w<VtY2wxdci*?Iw$Go2X1NHqeUu6>BSLF-vg}KPlw<AX$3*Qh`gPh{0$O-rk`*o`t<Jvz)|LxaJ*JnA-kGK!Mdaw%pTOmjI`!)DiSD~MS*e^wY%_Lu_<vH05U-GHqeZ)RW0oP3WRHtBE#rG=uajC@lPhtKmS50z+Xy!k^f_==ZfS-nZrHnrNH#j5TP;S6_CYED;0+27fWiZK+{E#nQxP(4CpNn2i$9=b<Uj|=23|~L_YxExtUzRd(FX*eE>rj6i=To?J5&pI`oWm#;{`m7a54nqwb8-jHRp{q@U&_GeRN*f8Uwne~;d7n*XbHy6{}|^m9KLuMpYQtqZRoR<^>Kypztx-O??FHMpHHCAKj$E)1pTNFj-viSKIS!gH=mb|z#qO8`Hg#Uzm6QjxO_eo+)7cu{~*@?7x?l;`sxA9OL4{L^};f&Pt1F$Ux#t!Qm)&WT^QH12>IFDk#lD&)}c+oI=k<Le`yQ)>3rTxtiXCUZbH3R8S>jvFS)^&roMr7xPW>&y9whujm9|<S0cY<J^HjNM*oxXJ|orF!oOY$zt2|qEmb&Id`=V0kt2lDZ(E7{I@Ak|705Y^9K)UU7&nRjjj70ajy{zo<>)hF73S4~9D{8c?nUol^z$|9^(Tt4KA&M+p$7T-%mVaNU5@&iwdlVjAM3;CE1`7-{Ihvj&&xINKU&9q&p|(Y?h<`i-;|A<vNiCBp<e2fiF0@w{VOl<{3c(`z<eE|;Ai8U$OBVNJ{P3V6r9@wDVXnl<g3qDBmZa;`Z-yR^=!oRr1U7!^z)**1m`&fzF}`2*7H~m_T`Is-isvc*W_aM6N~<Nuf>QW^kWTQd0LBplyc-8k21NBN(1h%p#i>dtRDU!c`q(Un9NIz#JFlpgvmWsYVbTSC9*y{3;VK*z9)Qr{yNm}S&sdRoMkd!y(RkByU#MY?`m`&|6LhsvhV5$zAv@Gmv|rbI@bHoG&$$;3i#5M>8OuuL_hV&F`S&v=Skdm^<EC@W2c*(A7Kaced%}J>uabNb_Sc?3;ObnAgqr&=BwO-uYLeusKfaee6p|(-cwBGE8BMXVJ6=ijHtA(6nb`G$IDW%7m^cR`pQ823qkl*|NU16X@39JR|dYme*f=R1`b-w9rK~iAdBQ_)Ku~`atbwroI*~g=9AOOi>V5EF?ktvC3zXSoca#AoLtS9k?X1J$wu8mt|vE9x09R5&D5RbX7V=b4)Qj#O5I9U$s4Ha$Q#IY)HUQf@@i@oc{RC$x}01=E}<?Vmyipn+2jIp7WEJ0Eb;<s5_thRks3ixB!^K)lf%gVR8O)$*@HTi>_Hwv9Y!8PcB76UyOF)AZ;-voepHF<M;=d|P99GVrbdy2$#bZ2<T>ORs!Wa{$5Io>vE+Hwc(PIFlIM}5sc(^^$+P(~atL)6IfNWUokR{I2T;e71IWJA;bdR33-xuf3)zYKD%pwLpK4F;Pqw4JLbfAYQ+trD$yQV|vK6@tRUmgEn^U`z&B@)Vy~y3ky{Qi5-egCrNOmMUQ>T%g$$``qav(XGnodq8FQP6cFCynsmyvVHh17C#A-R-VO)e!@@@3?;)OxZ}o5*X)4b*0G19>BL8+jvnGgT#TCU2r{Aa5c!QtQZ#<XY-#axHlkwSv5gyn<RnUO_IR7Lbd`dDJX&9yyb`fSgHAqb8Em$n&XT<oV=Ksy{iDJc{Z;9z}Mi4k5df2UFe1gUPN`Z?Y@di|R-AB9EkwCyykLqXv`5k*84Skf)GmQe((7$&u7pawPd}>O8VhqsecR!>O~$;p8{@GV)Yv2ze@bGBt=inLL3SK%PJzL-i$(A^T8W$UfvjR44Kv@@v%o<k!gksCMLj<UUkuav!n{)rxFG?n&)J?n$<wnv*Ta-KgEk-N=^I-egO%E!B~1OYTc`Cif)|pazl$kS9`;$rH&s>LRj^ypWnpUP#WN7Ls$wOR1&grQ~92CApYf#+Q+6I$mKj%*^e({HOnN`|U^3J~Uqb54hj|rs-q%%fIR0v1z|Pgon-OX55pG%`nFUlJR5+{{kA`qY3'

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
