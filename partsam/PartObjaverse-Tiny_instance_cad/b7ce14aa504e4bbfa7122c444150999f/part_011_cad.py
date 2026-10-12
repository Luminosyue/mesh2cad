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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_011.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_011.stl', 'source_sha256': '428141ef063ffed8100326622de441d6034bda04ea7aca10e12f7c87d6bef7d8', 'input_faces': 282, 'input_vertices': 211, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.03406340628862381, -0.13510477542877197, -0.4639546275138855], [0.08085526525974274, -0.03995850682258606, -0.11698536574840546]]}
GEOMETRY_BASE85 = 'c$}qLX>b-*7VVIbg#;49nt;%31|cj7NWv0rwh#;iWM3rtq9i2BW)gy|X}|!oBVjY3AAu}D2q+mrWN9J@sGu?qP-9ts<v26S4;?IYbdYl1>w8{L-%O@zYUZoD_0Bnc`@H*ZzwU2I#;5uRwAAR;Nt-=u_=6NdWrS%hwZg2tg52k_@_Wx;xWrG3uyy%T<Bqh+W5-YT(+ag^F|)JspUaCGq{j@&PK=4wW3m_I735{k&sdN*J4@=xnRD~Agr1+1xiCxc?(uPPv3kG9V)YgJ|M+SmN-*jc9(YoW=7EpOFNo2b5&DH3_0&Sr)4s8FD<X{RZLd)NHxagOe721AAzv`vEI(%J+SZGt*EF$pZ|{?ofAV(2`ii%0-CP?^`l-|8)8i)T3FL1X=b69Rtuf7e?LF>)i|bn8SzGr!4B`3p=bdnk&Fj<&-MoK-e9~J|J)hrT{Zu}Vj=rgU-)~=&o_+3+<XXXITi0H>OS*O6)_rxGsQ;xuvO0}|0P^YbfX|CQI6CSy#)NPk^LoGCM)Mxi%G`CTe5Gq&mD{@BwHehjAh68cf8!5aH>Z1TUHdhX>sXg(-B#K^7edS2*Tp#2g6l6Xvh($Q>uueW(wy`cj#7SUFw@NstL=Pi;5wT3)7HFBtjp2st;?9vp4Fpt&!0N6dc4i)x_IWsFn@2^O!E0Lwv6q=do#F>I?dx7$Y*7Infp3gwb@)(*FA6&=|PEQ?)%j1pUrjnsC;kKa8{?MZ3g9+rLa2nIq6JSeXu4zL-$M1v@-X7@o)MkuhDhC8^rZdJ4vsj=ZUv=B3qZrx00rpx%aJ^Gr2)s&u>cl`{``oYHe~F)QwY<n6CDZK6xV5Gj2BJ<2mNbn!|L}H{Zbt<Z~yN)o(8KFkSV*dpectmAmM^zO$V4%mu8U=Cur_D}Qxe>g(R1RIa~tmG*z(GP>XI7O?%Gzdeice=TDB-}k{3uA@$Ke-Zf<7xO+K-_hZt`mBX-<o9(T*HxYR;FWYgcG|_SJNlq>XaBStOFl<R+4WWX+0o%+<&GhrvlaZg)N2~uk0YyDol4i1-aBOH<9TI<o!~m^_kFgT>v*nO^WWq;?sucpVWz7-8wq>4j^~VL%@L~eL}YnG^*DOHdK|r8J&s<l9;G|=e6yG9_3E)!ep&9`hrYY(n6CD}dTv`$e=B!i7p=t_rmO3#Un1SS)4IaFZ#{|InC`sq<N4|6xUbdo*_YYAg5588ztan1D%|@=<tyEJ?yX--KEK9Rxa(K%%Su=K-+A8&Ph@o}-M2f5<*UBwM^f0lsz1K?G@2LBXYJvuOn08=86`X)``qd0jdaS#bH=!}h3o2b5#E>0+y!i2r~gV<pEuBd<A(xPkLt71o&I|^l23ri>Zz}*>tfz6CZEm4+y~do(bfH~uGf1Nq~rZj_02n`n$@q@?4bPgQ>5ehulnQt>seNh^SR}n?<(B)otb9R{X6V_h5J6TPOPGJWjCpG=d0(Q@qKuuJ6}C-&3!#9-S?@Q*XkBm>AoLTpDk-B<*Vnz#hv6cdKBsEInZS{*WvGc{`~zI=CAr-{q!vJSA8?g9Omzdpm~kUeX88+HQpUa^WGj*#nwA_5aoLemT#6kPWgGMEZ-VAfbusTu5#CJO&v;g?ys$K*RO>Pqx_gNEMJRDBL9JxdHz?V8?!#Ia<A9Zegx$&_zTm$6$aN;AFflrwdx+zojQM+c2eqA)e{%(`MNf<?7p6#Y3rWkBwN=a{h99VIMCL`_X}J1txl)>a|yQYDG0E2&kKuf-TZhM%h&oYwRL^oP+PZdHRk%)gKb@Wk0YP^%WYjN8ENbKfGDQ>Rt+Mb#2~8YbP=s9ZUnDW=~%D1C)(D{6{{PpN9n2$svh6aVyY+9p!~5vUvTTHepQb*a6PZH`2#y&%Pyt<OiN+)SUq01b>pXG>VIk^)15m1(T=Xm_g>Z?HLs(iPUT~sJjkw#sz>RnKYD4foo~EU!TMm{dT8f+ha6`0D}SY{I>q-X^6{(Y*HQT^9d#<*thqw^BdN^C(c$9>Z$;N7?*pp;%xJ3fVF=TmeV7qSb<X>a&1?L<#d&*-zsIhZ8Q<L2^>=?_KKfHXpR@Z{^b7A#@sGCd3;vDw;nl9>f8DRvt!ri!)17&*cd~Ww_JCUVzEb&Cbdy?lAJn|&mtnPRe_B7-x{(uE>#kpG*TeSFdbO%$_Y3A#x-;+87+d!}q1U>vyWZ>p&FkNVtxNSsyV{M_seC+}y4Sk*o9d6*syFl3{v6D7Z(R$j^W`9WAL@VX%lnCZrF(9Nv3z6iRH~;Yn(}Xk+q$RoEatCtvwsfN`B?|*=Y;^e-+z9d>7HkE$miTVs{h+I4eG|a*33s+y^#5M7vG`&B<E9|2|D#BdI+sIw2<mdjcQO=^C}<hkyWHW=xpo0;k_xpVlCAZ(VppM)-mem=$>>PrwpXNefJjgvGwunSIFs?=RP>yRMTXHXf3tuOxI74Qj{+>HvAK0ZvX%8C&<M3|Mw@zXGIM!h{zG~yohH+%mMa*&ld5bh-~0_;0r|LipU4f0+;7!z;g~fBu^JHO~iEIS>XBbei1kqe5Qy@5zhh70G}^nv4};$dEg606o@DUo(nz;=S~C81fL1-=@`?27vbFbzy;uoffoT6g69D*23`n01Afz7^GO~lqNCiBz%9Vr$^B$+A;MAMa;pT12m}rX4-pX{qA_qVcx!lc1a1p1z1m=2Ikp6D0`CCeQ1E8(4gwAXkHopb7@GixVJ#uRt-;%(=61l%z(cXdroe5$Loi1$a0_r*YhMw)fjfdXg?Bh`6nG!kx+RVWm+Ne#(JKIJZG?6DiSP$*4Bipv_66<)uA`Pdz>k1yI5z;;54;hu2J8<W2;2xb2s|EseS!Oc$B0M}@i_2f;He^pix>g?6nL_T!6FiYQ^325=pmvfa2N3Y@JIk21}?n}%qzz@;8=L~03HJVB)kU$_X3Z@Trt40;JvVxuE71lhoR<F;3vU{V2#PZ26$I^cL9D3T-KT-Vjyq=crv_GfS&>%<yyDIqrv4m`-ylII1yZ~v%81^z&*heaBdRt2=L*kWfbt^;E&?m9>Cqf`vE@+JODfqxF7If@X_!~0v-k4Uc?h31_5^fm*Yqm?glQSvxuR<-M|N7Y!5sXyg9T8;11xea6B4gH{j;L9e|_3BV5NLaDKGQD+0JP_zDp(iC6->99)h|UDyPdu}Z`;U=w@^#udQJz>7qzguW79D{ySJh&8|__)6gAz^lQFT*r%W-fDQQfu?*Ve_F&?5#xc!fy;5C3r_}@F;&DA;K|@m!(%GODZpcJEDd-ZxI8vN#3bO!;A4Qt0Z#x=a~)5^c@y9@37Ybi{1p)|izo(O4=%^GF1!I;#zqnAfH#1@0*{Rt*8y+Bu`R&s!R4{dBDMl=0N(_>9(XhO7T57DIBzq&wn9_BlD{URM8q!O-QfF0>=CgO_zm!*A}U23!B`IL6>(TZ6>u5&UU-xMmx8~JIrjkX13!d04g*(!AB6W2-~-_MFxP9qhrkbDEneWg;H9W}Kkz~D3aqgb_;qkEyvu-hgUedCiFg&b1iTX7<-l)%@4&kE0B;AE>pZT>KbaCf3NF`KEusdv3cLj8ZUf#4z6Z7J0Nw?D7~WMFt6lgw_;JirjrnV!9mU)=m~T5gw__fOZ;JRt#0`ue0ACUDsfZ7OKL)>noJ$zr2fmElI^Zkd^7u96NPHdqs)&z}{}Ilq!#r0p*T*<^73bZ=xz|zaO~egXZ65+(0=@xU2Yv}2b*?(<Fy6$uS8+^oOT-xwXMrz(pAhl3h+5z`!B2`fE#e*Ex4<uoI4|NH@O$9z!s86^@4!!CPU$&5)vr-Y|Nr!_C;xhx_6I)qKcdt>lYd=wpSe~fIbR;fr#6<K4aJAVM)nt_CGuTQ`zORYG^z'

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
