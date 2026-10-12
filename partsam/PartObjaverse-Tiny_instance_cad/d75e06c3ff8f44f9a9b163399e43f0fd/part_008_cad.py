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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d75e06c3ff8f44f9a9b163399e43f0fd/part_008.stl', 'relative_path': 'd75e06c3ff8f44f9a9b163399e43f0fd/part_008.stl', 'source_sha256': 'c22e35114df210dc8836d144630abcfde53618994457dfe22199b8b7b956a739', 'input_faces': 192, 'input_vertices': 184, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11823595315217972, 0.42271798849105835, -0.02930658683180809], [-0.00039539486169815063, 0.4999998211860657, 0.11389203369617462]]}
GEOMETRY_BASE85 = 'c$}q~3sg<{9>;e{2;-SNv%`>t@qP}Qs0h;-^43X89ut)^LT$Y~^A<u*d8E9eQk1b7TxJF{%$V^ShjocDUNa0ccW^u3-*@h<yY5}<u6xf~dwoCWdw%D;fBXO6kN+uOp9*$$6?wTR3mQEB$*83$)~%XSSBVM=pFK4&D572HthqKyP59Q=pSpI~$f3StY?LTvUaQGL5rN^YdaA8@2X}AfuC@xE89qBaAk=?m_~am~?-?*7BB<1l2nm=KRQlevL-)?^YNyuj>H_tDd^wc1pdKFZ>G4w4=G4C4w^Vi8>{RP}lT%0d#>MLJjb*lJ*7ugB^N+#*XfS+r&c~bZ{f$%LEB!p-n{K?`0>9>-V$`QBhHvq4-e`TVHd_f__llLA756q<-<y}06ybZBm&K1SPJuu89DMz!&*3Y1X7p*cYa_mI{Tt}>W$b$FFVsPDQfk0g&qSe5MU6g+&%YTV^<(_kp`Wg!;A;nlz*o+OpiiUgS4Z%@F{>r#_rSGyKXe~_BR^66f~XA`w{%zWo1K=N?~~V{&w`5Z^}0u;-g5(vODl{iMBboBQvb`1)u@XeBmP%+;Oi$Z<G3u}ohiWgzN~T+{vTebS08VOZ<M^1`nK+<H`y(edZ&h{R|e$bxXgRs9EKm)0KWN`3#+idnOET}X*J-hCCL~c<!YhSZ+Dd(e_Q0}4;{t7(g?nGEett^%`f@Tq}uRJeQl9rKK>1SZIYYhyLn^W%$fsyeWoLPqlUBO_?6^g|F^2cw``2U`0F8Gz}JJDOa86|jHhYt@`La@47r7V@_Of?U$=Ppip3Vb=~9Dy_*ZoJMn(dB<8DYU{QHxoJ~aCW<doPQF6(RO_DcSwormzf{oTd?Y#{2*KEE9<>l+1UCI8ze2ch-rOZ^%4xqKe_)SA>1-^E7!?9u4c?BXCf%ND^mAIn6a#+Bc4(C5=#*stlh$KkTR=679=SM!$r-g*e%NIe8!Uvo?PU-m%iJAWthIR0S)bl@fUdZT{GH=1{cuMa;a^_4CmM?KU^a&ogJe?^J(xhpdVIZ=s{^YUvsf9|S<$cc_ASFfB~fIcmk=1TqRK$-WL6R20yJf+_GiR9;1MZS4dd+`%r$Z;+D9==i7Sp1Rxa$foWEIE}gAHcYce<s&m$n+!FPxKD>#?7bFPvWip=>PII_}ZS=@GXzJNq%@6_<G(?$T2@PBS))Uupjkr-%5REy922IX0`a~4`qIz=Iq1#+>3;7bXp=g4sVcSeqz}t^PV90t2@1qqW_|O@U@e_%lyuMgdA<-MDeHI62HQty*Q2-8~Do2mdG*fNJEa^BzZ6D%`P$y3$MVpoR1g(#UmN#`#H!lPCJP2e_oC&D0mM(caGfy|LAve|L@bc2z~nWfN!{8lX<b5i+a<9lx)<G&6E63dS|1)<Ap5vA;;x<S=df|e;fEl+<G~#fq&bL&#%9~8}+-lN`B3=@b%_inK<5@nKF+zlQL1CvU(SMrzkmZYj=XL*#_=J&Yk|^Z@jh>#}{~R2lnedNcwy?4!*uPemioq>Ph|2+79GDm?eJI7Ug_JP02w1azA;Vy1Xfd>hbXP{BH2gk;*aj^Lzw+<+t_n9LzY1dehR!>FCF^ikv^2yKTqkL(joiPCbzPM;@rRIHkbX;vVDrRhE94fzR#Rz}NQ$NqvDc_G|KQDfJ#n(oa<v_{xFZX6%>GUvsBB$kztm+XlbUeaRoHB3~&ifUn!Om-FqyY^hI<g0HmAlJg|@UE~|XK9u^CU&?)EKxR5}6mQ9|a2EAiC07}rk{er*)2FUH?=C$rF6$e|H^}u8^)t>x<CP(P=C5*p4z|O%DUn>KoU=u}R_ug)Jv$4&QuI>BXU03S-+mrazvm)y^soT*X|$B}i#9w@`VYHi#^;*~;Om*ua($V$pigysGx)~Uq0*<@Q|W(m7S=V&*}IbOk&p2-1wWDX%e0ZGw{*KM_4{JQuXS6-;nyzWzo-FUuYMCb>X1y%`*S?Em7W{mTWs#9p|6nJ@U>&PGLMhzN&j1u<vD*kN7gN)vXO5N8zSqYl~-jv*{9Ka4W8%P+C$QRt!vxL`o<?W<T<tQT83PwUButvE%*8LCuF`7nu*`0K=xZLRnF(pxAC0Uryi8&vhpkP%_n=Ll-;kA(g^)qBHn|qbdvG3+#ZH`H{Y{?Z*aX~Za)e6N?@P$Wye8JTZbHTW3#M-F3Px>URH*$-HL{<bNypn_m}HBHdfXt_2fL!CN9JAs;g!FsGW?F<Na7EF6Z<7(F)$;yiy;Y!}`uxn;?BUR+M`C2C`1v_=Ox-^;I}7qyFnvWzQcYuMzG)=3b{|J!RaLKF`d?IP1PmS75(u9?E*M;T-s;qB+SjK0nGhoKM1i&m8z-Ir1Yb$bI#E^<BuT8UbIA^OAnLoRQ~C&!tP?7d4do^N~;Gemh~f_>Zg0eJtQJ@y}*2MnCI)%H^nUyceOL&(man$5xX3_%})Li+jrRVnAG$>}N|N`aID|_PbP-=SXT{Jo10{mwLy)?veQ#2Vc)kmwfw*lK*3F9CA`0%5~)Cc|^WfvJmxeMoa#m&)HrF;A^*=%5~lOExxa-!=?VQgWP967?1s#JQ~6`rZ~!ZKK3uNzt+ce_={V}_3rsBzMOCGD*m&!7)Nb?IDDmU9l6gqEQ4>UX_ER=RiyrnDWR;dt<t6cEEVe<_3NJH@{N#hF^)zjSNQtr*3y5_Gt7r&t)uwOoFzYNtITW1lvrqdRq-cGODgMYHuAenITj)F{k{!+qsU48%pc@<>l|8u@9k(P<70n6v7G;^u{>Y;w?>Y>b_#qW%uUt_8B4I<Ge-AcP;MS$yfKf;gGuvIug#J3@Kp}R!8jEYjlPbj%6V?*DC=0y)lqVtjuSuhBG$vos40=~8?Th{v<yML(zri-qlv534_+bb-t?EVQNMV<tfOYwV%@7aJA}axj+OOBvJ>(R*T`A$e=L%mZa1YqA|(`l%XH~~xI1%_XJEgMe$vm>E7E7*9@9|oCdZ|YoQ&TK`tiq8QD5Vf<c!J1dS0*Q6$JmnY4P24{O-_G{+JBEv-}P+&C1P}<C+3ro48M|FI7Q~Qn-7P%=;1XyD9nQ{NfYhAMn8MApLwy0Os>snHTk@D*X>m7>#<a8+EUXlAnCzqjKZ_YNq^Nd;V}R`i#$)aSq=gzwc&0^+5flH0giJ3F*gsbszZl{C$)$T7Ey8AM`+uB}@8@tC`=|x7=TUI;%fS*Q=C%rF5&J)K!85%KYiaYFb}^>c9Wf&(zNU-JgDXbo_t+^y6VYM(gRo&C0!~y~(}EU8vp3UC14%oyi@@ZK&<ZZOF~3?&RiV7pg1Sh1`_dlH8Q+OnsN^OjfC_$SS!R)s5VY+=AMc+=ASi`X0G8xgE6=xgEJ9wHvu3xhu5?xhuIR^?h<ravy3xavySk>Hu<o@<6I5c_7(~>P_|{526kx4<h?ehmd{9L#e~aL&+nk!^tDa<EW#_<H&*3N#sECG;UU&PW2~SHJCh|97>%^4kd?EKPHEhBd9aU5#%W9Y_e77lIKw8QRkB9krz;7$P35|sd40m<V0!$Igz}Cx|qC#oJ?IxP9~eF>&a&Fc4|6#J9#&CCwVt{KQ)uQpL~eAhkS^fN8L-#BOj*bkPnj!s0YXe<b3Kray~hinoZ6nAEfRgA0%f{Gss!w9n>`P4)QkYa`HCvGU_7oGIA0%o}5J1sj+08Jf9j(o=^UybPJ<KQlrU{<PhpCvQ;ONL&#&OACay4A$bgW6!io0D6${bmu%IMWIytF>R7T>P2}<9AZh^Fs#C~8<Qdd3au|<u1~)5DriPG1cnp)NqsWuV6R3V<KlU_%8bl7_KCHaCblXz8rEs(I2I^Mw2J#wiR^C{;t)-??w~|xIo2XmJo5<^^o5}0QE4f*DRq3{Zx|+I~yqUdP+4{06-E659$hKrVYDKag*`8X7Y)`ICtwOF$cA!=zJCLhUtCOpd-=WqZzeBD`twpX$u1&2&u1$8N)+0NT>r)$$>ysOCvvT9otqHXuwE?*y*@;?@>_o0htwZ+pv9YaN;XnQB?w>E+Itk_ek@v6PEWhk4`^`6{S^roB`ubF~&PnM++T!9kVm&J5?@JWD{Q'

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
