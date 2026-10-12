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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/42e5ff17de214f0d8aabd509f090a46c/part_005.stl', 'relative_path': '42e5ff17de214f0d8aabd509f090a46c/part_005.stl', 'source_sha256': 'dc481eb21573fa87c53e3b6aa503dfb1e77943cec62ffd1d85f50ab044906b97', 'input_faces': 364, 'input_vertices': 219, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12876494228839874, -0.4999998211860657, -0.46769729256629944], [0.10302960127592087, 0.36669984459877014, 0.4762924909591675]]}
GEOMETRY_BASE85 = 'c$}r032+ou9>yP#a0cZFilWkp5RQZ^;l74bFn~dBSjdDhF~|`TAlxzvMvyxRB;iP!gc}kG<PMNd2sa7}D~LhH)pg7Dq@>Dqaf|Ku@9)iYznQJt+8yd&-)}zNyna`|s}d1j$1ji>pEm5&oOaLDZ^0Ok02as+9SKY3MmrXFS-5CLE!Kp5{t=ooZqnF@X|-4)TNO0Nu{b&*sGkxvAf``Huo4s#m#`!uYGGtt!W;+pM@G$G?9lziu~Ca0`u7e!y7vuMLOTX4Yn1=-(@-yhI%}0yp{wnWv@f~329Nus!sM%!wZ9;36@S;4uU$^6w)m|de`e0d`9qru(ym7S&Q^}QzI^saMzz^jlKk)ZN-uno-ZjczMt+Y656sUMzPp@lN7wlBU59R#nSIx{Gj3bjVP#G!{r*}F<!>K1^sX<TMc=MA`_8UAsb0!2&(-+y?O)6*H~Y2;uiWvKUifl)R<QoIukr|Al*e8ZUrhNpZc{m(8@7Dm%Xcjwc-HJ|?>xEfE4}bVdUo|<9+msaZ<hAAU5O#z-s9l|b3e+y=ttqZ$I0du_kH=y|3MM?A!BpR?JwF*_TBB4o^yzPpPhSgF#rB_eHyQJMK%2211@l1*;=d8?AsHAFLPhpdY0;|)k`N|`*rMj?z<*lsx<qy<fJRyxAzY)o}2v!`AXZ>m6Xqq)2b|fXvtM7Ps3&<)PB$YaDa5#HI4Gw9aCZU)zIlxRL(!*&zXH&$VWzbj(0k1_O+XBsa|$Ra=F=8VrNl1xaJ=&HT%wiYc6r$_V>4nEzhm%q;^p6*A!5`AvcWlF=_>sr%gqb*;mW+uTlPfg9_<+*T)&<?6Tt=<&)J=GyBR%GpXIQso|$6U67hX`BZ;P>79|w%gsJp_yV=3>lx$y6~4<a%V?j>;!?BktobLkk9Iwz#FGEUZqz=u$gm<yKFbDE`zRS#PMdw(!ysxOE&HdF^!<eZ^0gK>$|;|wkIT)zebysNueM)yg8Zh-v#C7mf2H(n$#Bi=+v+x^@nBovXXM`}bw8D}cjvQI-?E2Q7Qgv~>*PP(lFF$(ew}>9v8<Gy+dcb?#qaPT^`m`t>Jch;gC$wy=N&ym<@vmOiP^U$H#f#%<&|Qy&w_KP{cVfy6j{<AsAG)7>C+3%zUyRIHKkW4oVGl7Z!c<p=dkl9&A#SnV7#Y&B92qOEjMIRK2h&dy<EMwlvw<p7b(4SLH<E%m-c)2Q91K|Hrl~2Rx|tR@lDjuu8XUvU({jMd+51CVv5PnoKkA`S#&P>%2EHbX5SW;Wb|)~$=PP#^=3C3&$gBCQF)XtX}d}5d`11POnOvh_U#*XP(RvAzs;w71~f{ieC}^AB0nXz%<S8Pjd{t{ew)#+r<Nv@pFW=Q*UI}9nSCwrJ9>|_kN;6<@dpG@KiacjwD^jD9KA<s_L0+OU#;9n{p*b0op1JSscF=|+Wv2H%|4qklloWtSJYt|_Z=SXApcOK5_;~`l|^RX`Aak7y}O@C^>Sq<kneiAl+xP@)@Wwm9)6elQQ11>7?p2R+;*y0*IR{@zQgOqW?zjPK<%mKl%FyC&c^rYx%PGU_LzO!)d=cGrIl*Dx668Nqxuz$qjt6jeqUww)ulPqkIr#ZsC~5U_qWpj{}@Q+Q8)K3HT$-ZZ)p73Z`Byjz4SPS>UDf_0r_94C1zi#=t%jv{<5dY>^pzXF!CQV?~EmVlO$u@_P<<c@f(e&_SAk_ubF+<x-ZKpeZ3S*daZ49V}6_ZU6m!hZ7q!}+pU?F^epFdW8UceL4l>5DFbO-iTTQ%PtZJLT>Vft-|X9t&8Bgs9?LsnDG$~)Ew$MpOT8Z5G3N7Hzh#+ywe1mOy;EnVTgua^g4*BpV?T?p=8rPgaa-^GmVP<=kj9(+rh3%k&p%<jzu7Mt{r+qhJC)~jlRK1u_^L0d9#66g&T&7w5&6y(tFP8xPCm;?Bwu^7HlO>pCr>Q<E8&ZMm)M`nzSy6;ee9FPepvR!e%Sq7oC{R#r~AHq))VvmU%S```>3z;!qtUTkJgIeA6QAglG$~sF+Tc`uO_W9>U$z`-C$qu3w-%~v85D~FTan%m)}R_mg7Bojx;|AU!EU?FV7Fcm*)rd_j&JAJ*D|d`0{+EG>+Rq{VmOh!k6bmRY}-L>7;pH`0_mO_N94V`0_k2e0iQ1zC6zh-)o+KZA>z?gS37L-)sH){$47TM_wP{d##WA>+PcF$?G+Iuk{+f*Ln?KUa!^l57H<fdH(=k-ajab*V5^`v_EnC(*8t=EzY3wN&7D0%lj_j%lj^OdTHM!e0ksHey+6d6283ea!&kuFQu3ElWt$yPdeY8yN}XI`&G9u?N^=7&@3v4v>z6}*M2xBSfz5x`)&AM`|Ui9e6Mo^e6Mo^e6Mo^e6Mqa$X`B3h<xO81bnY^#HvO6$(PPY!k5oSTFo!yd!4`F%jYk4sd2VZ9_zVM`0}|@`0}|@`0}|@`0}|@`0}~Z{apE6IetkF<s+S!-M(~QX2qrC%ja?7%ja?DjY{(6^S<!C&ik)kFw#r+2JCNRaw(m3{~-I~{(-HF$)o(G`w-a|_aVZU??Yr?+=sCB7s;3JVeF;xG!J^+|46>L&ru#8D7BOy_e-)b?w5ow-*?HrXa`q2yRpAC-`7Q0Zc#hk7!kj{DPueuus{|QWx7J;CjSWaeT6zV?7zA~4eb^7|6ZZ`quBKk{1X860|!E%g8G4<0ylux0yh9Rfz|~-18oMa3vLE(1g!&Z1a1zk2YwdX6j~456x<M68{825G}Is50@@hr5B5h}a9*v)+j=~&$4gKr^lh*c{4s*_O$6s#(AD5u;2Y32;E$kdp=-cv!7m~>KZoGl61p0^8s%$=cph~Tb!d!u32o2<{4|2|3kc5dLY?4u!Jk4u27e0v9Krd|2+nt)H^Fzn_n^1H_rRY)Z-7M`eTLwC8^QT5g7YT`&hJ3ig5LqRg1!iD1r}qQb0C6q0Q5O<0JuK1CAcNpmvdh|y6Mpy8Vv3Y?gi}(?gj1%?F8-#4uf_Chk-+(9l)XB9?&3g4{&#AdvJGf9|Y&Fdh~-1KyVI$wg-oRUx5aJUje@i?EromtUx=06>w{4Cva<U8)#>68*p1_Ft{za9kd&`9k`1g1EKw)-N4<@XZ@jr!TrInAvllI;|=Io=wR?z@F-|s@F?&|Xm9XH@Caxx@Cfj5XixBP@Gxi?co=vnG!#4(JOtVUJOpfmb_d(QuR{BPUj>IFI1hq$1&eVr2*G&_bTl|ukJEabL2$kREdyTwS3^s|)!_5c67YF&6|@*!1+Ih^fh)lpv=FR;E1(773UE1s^C>;{>2X4j9Ox-<4)`Fn0DKU92wDg}1U?Kc0v`q+ffj?0fR92;z(>Kyprznr;N#FT@Nw_~=xOi)a27NdoCV&E;H>JA4b6w<f^*Tw`3TM*A~>IeUI3p1UxHSHFM+Q>&x5akuR*K8*TC1ImEh~(t56Mm6?_?50lo~r2rUO+1fSI-4|)<>4(56a%=HBLBzQkG6TD52WqNEua888I1Sf){m@(&YeGNJj+#fm+!8rmt6C44KhAsm~gO@|MftQ0fqVM*a`jm4vbR&2p(q|($tI#cA6)eUQ=l7wB;P=5xp;6$aV27zK9LzH>bDp5bJUu2t7l0>%CqWm2CxItJ<G_=_Q=p5$Q@~T9@!+Z8Y0w1lH1G`QV(<*G9l?2t9-E;%po_sf!0FHga5^{*8V^nb?}9D@?*i|H#({T&Q=tpNso)go0&ogA89EP~4Bn35JQq3vJQqBj8EeWcW~?)_;E8pIvkf|ddDbb;L!c9xXI<kw6gr7{)<Mq0pp%(r-Q+wRI)!=GS<WM%Q<-O7<~$NQjd|8_&ZD3+m}lMRJQiwao_zx6HxQg1&?R68cq#LY2{HaT^Y>#nGz+?!dFE=)2cSEcXKv?w9GcENYXRqD&@|>*J2)SO?qZ&`hVv2VPUcygI3I?lGS6DZ`4BXPdDcG82cgN#vsQA>fo^A>wUzTe1m_Q+bHN{g--J#FbDagAqerYBF?u9HH$h{;o4{KUoZr&pPtZtcEI1bVMj|+mM{pK<r#UFc96WCpA_ip>WqK2lggSA}Fx4@GdG;V&Gocya4E!b&x(S>K-VfahJ_*f3aNYym3f=?W0DTL*0X*N-M)MJzXEWm*@j5g1gZ;pxp|ioWk$yCS^B8C(I1+6-2Elm{G#tEMkN5OgrN=sa=e!c%Ij_KX&Jp3YY6sT&Pk$2U`8fH-hUE|B<X>8^fy}=gspsXs6p9G<=XV~gw*HS#%uV@8iTxYEEGbj'

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
